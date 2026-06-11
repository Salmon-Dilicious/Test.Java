# -*- coding: utf-8 -*-
"""
Wireshark 封包安全分析與入侵偵測系統 (NIDS)
支援功能：
1. TCP SYN Flood DDoS 攻擊偵測與速率分析
2. DNS 隨機子網域攻擊 (NXDOMAIN Flood) 偵測
3. DNS 放大攻擊 (DNS Amplification Attack) 偵測與 Query Type (ANY/TXT) 進階分析
"""

import os
import sys
import time
from collections import deque

try:
    from scapy.all import PcapReader, IP, TCP, UDP, DNS, DNSQR
except ImportError:
    print("+" + "="*58 + "+")
    print("| 錯誤：找不到 scapy 模組！                                |")
    print("| 請在終端機中運行以下指令安裝 scapy 後再重新執行：        |")
    print("|                                                          |")
    print("|     pip install scapy                                    |")
    print("+" + "="*58 + "+")
    sys.exit(1)

def format_size(bytes_size):
    """格式化檔案大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def format_bps(bps):
    """格式化網路速率"""
    for unit in ['bps', 'Kbps', 'Mbps', 'Gbps']:
        if bps < 1000.0:
            return f"{bps:.2f} {unit}"
        bps /= 1000.0
    return f"{bps:.2f} Tbps"

def analyze_pcap(pcap_path):
    if not os.path.exists(pcap_path):
        print(f"[-] 錯誤：找不到封包檔案，路徑為: {pcap_path}")
        return

    file_size = os.path.getsize(pcap_path)
    print("=" * 65)
    print("            基於封包偵測之資訊安全專題偵測系統")
    print("=" * 65)
    print(f"[*] 分析檔案：{os.path.basename(pcap_path)}")
    print(f"[*] 檔案路徑：{pcap_path}")
    print(f"[*] 檔案大小：{format_size(file_size)}")
    print("[*] 正在載入並解析封包數據，請稍候...")
    print("=" * 65)

    # 基礎計數變數
    total_packets = 0
    tcp_count = 0
    udp_count = 0
    dns_count = 0
    
    # TCP 統計變數
    syn_count = 0
    syn_ack_count = 0
    syn_sources = {} # src_ip -> count
    syn_timestamps = []
    peak_syn_pps = 0.0

    # 偵測結果狀態 (動態判定)
    syn_flood_detected = False
    random_subdomain_detected = False
    dns_amp_detected = False

    # DNS 統計變數
    dns_queries_count = 0
    dns_responses_count = 0
    dns_any_queries_count = 0
    dns_txt_queries_count = 0
    
    # DNS 時間視窗統計資料結構 (window_id 為秒數)
    # window_id -> dict
    dns_windows = {}

    # 時間戳記變數
    first_pkt_time = None
    prev_pkt_time = None
    active_duration = 0.0

    # 峰值 PPS 滑動視窗設定
    # 使用 10ms 滑動視窗：每收到一個封包時往回看 10ms 內的封包密度，取最高密度作為峰值 PPS
    RATE_WINDOW_SEC = 0.01  # 10 毫秒滑動視窗
    tcp_ts_win  = deque()   # 儲存視窗內的 TCP 封包時間戳
    udp_ts_win  = deque()   # 儲存視窗內的 UDP 封包時間戳
    dns_ts_win  = deque()   # 儲存視窗內的 DNS 封包時間戳
    peak_tcp_pps = 0.0      # 已觀測到的 TCP 峰值 PPS
    peak_udp_pps = 0.0      # 已觀測到的 UDP 峰值 PPS
    peak_dns_pps = 0.0      # 已觀測到的 DNS 峰值 PPS
    
    start_time = time.time()
    
    try:
        with PcapReader(pcap_path) as reader:
            for pkt in reader:
                total_packets += 1
                
                pkt_time = float(pkt.time)
                if first_pkt_time is None:
                    first_pkt_time = pkt_time
                
                # 計算流量活躍時間 (忽略大於 2.0 秒的合併空白間隔)
                if prev_pkt_time is not None:
                    diff = pkt_time - prev_pkt_time
                    if 0 <= diff < 2.0:
                        active_duration += diff
                prev_pkt_time = pkt_time

                # 1. TCP 協定安全偵測
                if pkt.haslayer(TCP):
                    tcp_count += 1
                    # --- 滑動視窗峰值 PPS ---
                    tcp_ts_win.append(pkt_time)
                    while tcp_ts_win and (pkt_time - tcp_ts_win[0]) > RATE_WINDOW_SEC:
                        tcp_ts_win.popleft()
                    cur = len(tcp_ts_win) / RATE_WINDOW_SEC
                    if cur > peak_tcp_pps:
                        peak_tcp_pps = cur
                    # ---------------------------------
                    flags = pkt[TCP].flags
                    is_syn = (flags & 0x02) != 0
                    is_ack = (flags & 0x10) != 0
                    
                    if is_syn and not is_ack:
                        syn_count += 1
                        if pkt.haslayer(IP):
                            src_ip = pkt[IP].src
                            syn_sources[src_ip] = syn_sources.get(src_ip, 0) + 1
                        
                        # 滑動視窗計算 TCP SYN 峰值速率 (以 500 個封包為視窗)
                        syn_timestamps.append(pkt_time)
                        if len(syn_timestamps) > 500:
                            win_duration = syn_timestamps[-1] - syn_timestamps[0]
                            if win_duration > 0.0001:
                                win_pps = 500.0 / win_duration
                                if win_pps > peak_syn_pps:
                                    peak_syn_pps = win_pps
                            syn_timestamps.pop(0)
                            
                    elif is_syn and is_ack:
                        syn_ack_count += 1
                
                # 2. UDP 協定偵測
                if pkt.haslayer(UDP):
                    udp_count += 1
                    # --- 滑動視窗峰值 PPS ---
                    udp_ts_win.append(pkt_time)
                    while udp_ts_win and (pkt_time - udp_ts_win[0]) > RATE_WINDOW_SEC:
                        udp_ts_win.popleft()
                    cur = len(udp_ts_win) / RATE_WINDOW_SEC
                    if cur > peak_udp_pps:
                        peak_udp_pps = cur
                    # ---------------------------------

                # 3. DNS 協定偵測與深度解析 (DNS over UDP 或 TCP)
                if pkt.haslayer(DNS):
                    dns_count += 1
                    # --- 滑動視窗峰值 PPS ---
                    dns_ts_win.append(pkt_time)
                    while dns_ts_win and (pkt_time - dns_ts_win[0]) > RATE_WINDOW_SEC:
                        dns_ts_win.popleft()
                    cur = len(dns_ts_win) / RATE_WINDOW_SEC
                    if cur > peak_dns_pps:
                        peak_dns_pps = cur
                    # ---------------------------------
                    dns_layer = pkt[DNS]
                    win_id = int(pkt_time - first_pkt_time)  # DNS NXDOMAIN 對払用相對秒
                    
                    if win_id not in dns_windows:
                        dns_windows[win_id] = {
                            'nxdomain_count': 0,
                            'subdomains': {},       # main_domain -> set of subdomains
                            'responses_count': 0,
                            'large_responses_count': 0,
                            'bytes_per_victim': {}, # victim_ip -> bytes
                            'responses_per_victim': {}, # victim_ip -> count
                        }
                    win_data = dns_windows[win_id]
                    
                    is_response = dns_layer.qr == 1
                    
                    # 獲取目的地 IP (對於 DNS Response 而言即為受害者 IP)
                    victim_ip = None
                    if pkt.haslayer(IP):
                        victim_ip = pkt[IP].dst
                    
                    if not is_response:
                        # DNS Query - 進階選做：分析 QTYPE
                        dns_queries_count += 1
                        if pkt.haslayer(DNSQR):
                            qtype = pkt[DNSQR].qtype
                            if qtype == 255:   # ANY Query
                                dns_any_queries_count += 1
                            elif qtype == 16:  # TXT Query
                                dns_txt_queries_count += 1
                    else:
                        # DNS Response
                        dns_responses_count += 1
                        win_data['responses_count'] += 1
                        
                        pkt_len = len(pkt)
                        if victim_ip:
                            win_data['bytes_per_victim'][victim_ip] = win_data['bytes_per_victim'].get(victim_ip, 0) + pkt_len
                            win_data['responses_per_victim'][victim_ip] = win_data['responses_per_victim'].get(victim_ip, 0) + 1
                            
                            # 大於 512 位元組判定為大型 Response
                            if pkt_len > 512:
                                win_data['large_responses_count'] += 1
                        
                        # 隨機子網域攻擊判定：RCODE == 3 (NXDOMAIN)
                        if dns_layer.rcode == 3:
                            win_data['nxdomain_count'] += 1
                            
                            # 網域解析與拆分
                            if pkt.haslayer(DNSQR):
                                try:
                                    qname_bytes = pkt[DNSQR].qname
                                    qname = qname_bytes.decode('utf-8', errors='ignore').rstrip('.')
                                    parts = qname.split('.')
                                    
                                    # 拆分主網域與子網域 (支援 2-level 如 abc.com 與 3-level+ 如 abc.def.com)
                                    if len(parts) >= 2:
                                        subdomain = parts[0]
                                        main_domain = '.'.join(parts[1:])
                                        
                                        if main_domain not in win_data['subdomains']:
                                            win_data['subdomains'][main_domain] = set()
                                        win_data['subdomains'][main_domain].add(subdomain)
                                except Exception:
                                    pass

    except Exception as e:
        print(f"[-] 解析封包時發生嚴重錯誤: {e}")
        return

    end_time = time.time()
    elapsed_time = end_time - start_time

    # 處理 TCP 最後不足一個完整滑動視窗的峰值速率
    if len(syn_timestamps) >= 2:
        win_duration = syn_timestamps[-1] - syn_timestamps[0]
        if win_duration > 0.0001:
            win_pps = len(syn_timestamps) / win_duration
            if win_pps > peak_syn_pps:
                peak_syn_pps = win_pps

    # 計算流量總時長與活躍時長
    total_capture_duration = 0.0
    if first_pkt_time is not None and prev_pkt_time is not None:
        total_capture_duration = prev_pkt_time - first_pkt_time
        
    if active_duration <= 0.000001:
        active_duration = total_capture_duration if total_capture_duration > 0.000001 else 0.0

    # 輸出基礎報告資訊
    print("\n" + "[+] 解析與多重威脅評估完成！".center(55))
    print(f"[*] 解析時間：{elapsed_time:.2f} 秒")
    print(f"[*] 封包總數：{total_packets} 個")
    print("-" * 65)
    print("網路協定概覽統計：")
    
    tcp_pct = (tcp_count / total_packets * 100) if total_packets > 0 else 0
    udp_pct = (udp_count / total_packets * 100) if total_packets > 0 else 0
    dns_pct = (dns_count / total_packets * 100) if total_packets > 0 else 0
    
    print(f"  - TCP 封包數 : {tcp_count:<8} ({tcp_pct:.2f}%)")
    print(f"  - UDP 封包數 : {udp_count:<8} ({udp_pct:.2f}%)")
    print(f"  - DNS 封包數 : {dns_count:<8} ({dns_pct:.2f}%)")
    print("-" * 65)

    # ==================== TCP SYN FLOOD 偵測區塊 ====================
    if tcp_count > 0:
        # 計算 TCP 統計速率
        avg_syn_pps = 0.0
        if active_duration > 0.000001:
            avg_syn_pps = syn_count / active_duration
        if avg_syn_pps > peak_syn_pps:
            peak_syn_pps = avg_syn_pps

        is_tcp_flood = False
        is_tcp_flood_by_ratio = False
        is_tcp_flood_by_rate = False
        tcp_ratio_str = ""

        if syn_ack_count == 0:
            if syn_count > 0:
                tcp_ratio_str = f"{syn_count} : 0 (無限大)"
                # 設定最少 10 個 SYN 封包才進行比例判定，過濾微量噪聲
                if syn_count >= 10:
                    is_tcp_flood_by_ratio = True
            else:
                tcp_ratio_str = "0 : 0 (無 SYN 封包)"
        else:
            ratio = syn_count / syn_ack_count
            tcp_ratio_str = f"{ratio:.2f} : 1"
            # 必須滿足基本發送量（50個），才進行比例警報判定
            if ratio >= 10.0 and syn_count >= 50:
                is_tcp_flood_by_ratio = True

        if peak_syn_pps > 1000.0:
            is_tcp_flood_by_rate = True

        if is_tcp_flood_by_ratio and is_tcp_flood_by_rate:
            is_tcp_flood = True

        print("【模組一：TCP SYN Flood DDoS 偵測】")
        print(f"  - SYN 封包數 (連線請求)     : {syn_count}")
        print(f"  - SYN-ACK 封包數 (連線允許) : {syn_ack_count}")
        print(f"  - SYN : SYN-ACK 比例        : {tcp_ratio_str}")
        print(f"  - 流量活躍捕獲時間          : {active_duration:.4f} 秒")
        print(f"  - 平均 SYN 發送速率         : {avg_syn_pps:.2f} pps")
        print(f"  - 峰值 SYN 發送速率         : {peak_syn_pps:.2f} pps")
        
        if is_tcp_flood:
            print("\n  [!] [警告] 檢測到潛在的 SYN FLOOD DDoS 攻擊狀態！")
            if is_tcp_flood_by_ratio:
                print(f"    [-] 原因：SYN 與 SYN-ACK 的比例已達 {tcp_ratio_str}，大於或等於 10:1 門檻。")
            if is_tcp_flood_by_rate:
                print(f"    [-] 原因：SYN 瞬間峰值速率達到 {peak_syn_pps:.2f} pps，大於 1000 pps 速率門檻。")
            
            if syn_sources:
                print("    [-] [可疑 SYN 攻擊來源 IP 排行]：")
                sorted_sources = sorted(syn_sources.items(), key=lambda x: x[1], reverse=True)
                for idx, (ip, count) in enumerate(sorted_sources[:3], 1):
                    pct = (count / syn_count * 100) if syn_count > 0 else 0
                    print(f"      {idx}. IP: {ip:<15} | 發送 SYN 數: {count:<6} | 佔總 SYN: {pct:.2f}%")
        else:
            print("\n  [OK] [正常] TCP 安全評估通過，無 SYN FLOOD 威脅。")
        print("-" * 65)
        syn_flood_detected = is_tcp_flood

    # ==================== DNS 安全分析區塊 ====================
    if dns_count > 0:
        # 1. 隨機子網域攻擊評估變數
        nxdomain_flood_detected = False
        peak_nxdomain_pps = 0.0
        peak_unique_subdomains = 0
        nxdomain_target_domains = set()
        
        # 2. DNS 放大攻擊評估變數
        dns_amp_detected = False
        peak_large_packet_ratio = 0.0
        peak_dns_throughput_bps = 0.0
        dns_victims = {} # victim_ip -> peak throughput
        total_large_responses = 0

        # 遍歷時間視窗進行評估
        for win_id, win_data in dns_windows.items():
            win_responses = win_data['responses_count']
            win_large_responses = win_data['large_responses_count']
            total_large_responses += win_large_responses
            
            # --- 隨機子網域偵測 ---
            win_nx_pps = win_data['nxdomain_count'] / 1.0
            if win_nx_pps > peak_nxdomain_pps:
                peak_nxdomain_pps = win_nx_pps
            
            if win_nx_pps > 5.0: # 速率大於 5 pps (敏感度優化)
                nxdomain_flood_detected = True
                
            for main_domain, subs in win_data['subdomains'].items():
                u_count = len(subs)
                if u_count > peak_unique_subdomains:
                    peak_unique_subdomains = u_count
                if u_count > 10: # 1秒內同一網域不重複子網域 > 10 個 (敏感度優化)
                    nxdomain_flood_detected = True
                    nxdomain_target_domains.add(main_domain)

            # --- DNS 放大攻擊偵測 ---
            win_large_ratio = (win_large_responses / win_responses * 100) if win_responses > 0 else 0
            if win_large_ratio > peak_large_packet_ratio and win_responses >= 5:
                peak_large_packet_ratio = win_large_ratio
            
            # 條件 A：大型封包佔比超過 70% 且大型封包數高於基本門檻 (30個)
            if win_large_ratio > 70.0 and win_large_responses > 30:
                dns_amp_detected = True
                
            for victim_ip, byte_count in win_data['bytes_per_victim'].items():
                win_throughput = byte_count * 8.0 / 1.0 # bps
                if win_throughput > dns_victims.get(victim_ip, 0.0):
                    dns_victims[victim_ip] = win_throughput
                if win_throughput > peak_dns_throughput_bps:
                    peak_dns_throughput_bps = win_throughput
                
                # 條件 B：流向單一受害 IP 的吞吐量 > 1 Mbps 且帶有大型 Response 傾向
                if win_throughput > 1000000.0 and win_large_ratio > 40.0:
                    dns_amp_detected = True

        # 進階選做：Query Type ANY/TXT 分析與風險分數調高
        high_risk_query_type = False
        query_any_ratio = (dns_any_queries_count / dns_queries_count * 100) if dns_queries_count > 0 else 0
        query_txt_ratio = (dns_txt_queries_count / dns_queries_count * 100) if dns_queries_count > 0 else 0
        
        if dns_queries_count >= 15:
            if query_any_ratio > 30.0 or query_txt_ratio > 30.0:
                high_risk_query_type = True
                # 若大量 ANY/TXT 且伴隨著大型封包比例大於 50%，直接拉響警報
                if peak_large_packet_ratio > 50.0:
                    dns_amp_detected = True

        # 輸出 模組二：隨機子網域攻擊報告
        print("【模組二：隨機子網域攻擊 (NXDOMAIN Flood) 偵測】")
        print(f"  - DNS 總回覆封包數          : {dns_responses_count}")
        print(f"  - 總 NXDOMAIN (RCODE=3) 數  : {sum(w['nxdomain_count'] for w in dns_windows.values())}")
        print(f"  - 峰值 NXDOMAIN 回覆速率    : {peak_nxdomain_pps:.2f} pps")
        print(f"  - 峰值單一網域不重複子網域  : {peak_unique_subdomains} 個")
        
        if nxdomain_flood_detected:
            print("\n  [!] [警告] 疑似遭受隨機子網域攻擊 / NXDOMAIN Flood！")
            if peak_nxdomain_pps > 5.0:
                print(f"    [-] 原因：NXDOMAIN 回覆速率達 {peak_nxdomain_pps:.2f} pps，大於安全門檻 (5 pps)。")
            if peak_unique_subdomains > 10:
                print(f"    [-] 原因：單一主域名下偵測到 {peak_unique_subdomains} 個隨機子網域查詢，大於門檻 (10個)。")
            if nxdomain_target_domains:
                print(f"    [-] [遭受攻擊主網域目標]：{', '.join(nxdomain_target_domains)}")
        else:
            print("\n  [OK] [正常] 隨機子網域分析評估通過，未偵測到 NXDOMAIN 異常。")
        print("-" * 65)

        # 輸出 模組三：DNS 放大攻擊報告
        print("【模組三：DNS 放大攻擊 (DNS Amplification) 偵測】")
        print(f"  - DNS 查詢封包數 (Queries)  : {dns_queries_count}")
        print(f"  - DNS 回覆封包數 (Responses) : {dns_responses_count}")
        print(f"  - 峰值大型封包 (>512B) 佔比 : {peak_large_packet_ratio:.2f}%")
        print(f"  - 峰值 DNS 總吞吐量速率     : {format_bps(peak_dns_throughput_bps)}")
        
        # 顯示 Query Type 分析資訊
        if dns_queries_count > 0:
            print(f"  - ANY (255) 查詢佔比        : {query_any_ratio:.2f}% ({dns_any_queries_count}個)")
            print(f"  - TXT (16) 查詢佔比         : {query_txt_ratio:.2f}% ({dns_txt_queries_count}個)")

        if dns_amp_detected or high_risk_query_type:
            if dns_amp_detected:
                print("\n  [!] [警告] 疑似遭受 DNS 放大攻擊 (DNS Amplification Attack)！")
            
            if high_risk_query_type:
                print("  [!] [高風險] 偵測到大量 ANY/TXT 查詢，可能涉及 DNS 放大攻擊！")
                
            if peak_large_packet_ratio > 70.0:
                print(f"    [-] 原因：DNS 大型回覆封包比例高達 {peak_large_packet_ratio:.2f}%，大於門檻 (70%)。")
            if peak_dns_throughput_bps > 1000000.0:
                print(f"    [-] 原因：DNS 峰值流量高達 {format_bps(peak_dns_throughput_bps)}，大於門檻 (1 Mbps)。")
            
            # 列出主要流量流向 (受害者 IP)
            if dns_victims:
                print("    [-] [受害主機集中流量 IP 排行]：")
                sorted_victims = sorted(dns_victims.items(), key=lambda x: x[1], reverse=True)
                for idx, (ip, max_bps) in enumerate(sorted_victims[:2], 1):
                    print(f"      {idx}. 受害 IP: {ip:<15} | 瞬間受擊流量: {format_bps(max_bps)}")
        else:
            print("\n  [OK] [正常] DNS 放大攻擊分析通過，流量特徵與吞吐量均正常。")
        print("=" * 65)
        random_subdomain_detected = nxdomain_flood_detected
        dns_amp_detected = dns_amp_detected

    # ==================== 模組四：封包接收速率偵測 ====================
    # 峰值 PPS 已在解析迴圈中以 10ms 滑動視窗即時計算完成
    # 公式：視窗內封包數 / 0.01 秒 = 瞬間 PPS（取整個分析過程中的最大值）
    avg_tcp_pps = (tcp_count / active_duration) if active_duration > 0.000001 else 0.0
    avg_udp_pps = (udp_count / active_duration) if active_duration > 0.000001 else 0.0
    avg_dns_pps = (dns_count / active_duration) if active_duration > 0.000001 else 0.0

    tcp_rate_high = peak_tcp_pps > 10000.0
    udp_rate_high = peak_udp_pps > 10000.0
    dns_rate_high = peak_dns_pps > 10000.0

    print("【模組四：封包接收速率偵測 (門檻：10000 PPS)】")
    print(f"  測量方法：{RATE_WINDOW_SEC*1000:.0f}ms 滑動視窗，取整個擷取過程中最高的瞬間密度")
    print(f"  - TCP 封包接收速率 : {peak_tcp_pps:,.0f} pps (峰值) / {avg_tcp_pps:.2f} pps (平均)")
    print(f"  - UDP 封包接收速率 : {peak_udp_pps:,.0f} pps (峰值) / {avg_udp_pps:.2f} pps (平均)")
    print(f"  - DNS 封包接收速率 : {peak_dns_pps:,.0f} pps (峰值) / {avg_dns_pps:.2f} pps (平均)")

    if tcp_rate_high:
        print(f"\n  [!] [警告] TCP 封包速率超過門檻！({peak_tcp_pps:,.0f} pps > 10000 pps)")
    else:
        print(f"\n  [OK] [正常] TCP 封包速率正常。({peak_tcp_pps:,.0f} pps)")

    if udp_rate_high:
        print(f"  [!] [警告] UDP 封包速率超過門檻！({peak_udp_pps:,.0f} pps > 10000 pps)")
    else:
        print(f"  [OK] [正常] UDP 封包速率正常。({peak_udp_pps:,.0f} pps)")

    if dns_rate_high:
        print(f"  [!] [警告] DNS 封包速率超過門檻！({peak_dns_pps:,.0f} pps > 10000 pps)")
    else:
        print(f"  [OK] [正常] DNS 封包速率正常。({peak_dns_pps:,.0f} pps)")
    print("=" * 65)

    # ==================== 風險等級判定 ====================
    # 共 6 項判斷指標：3 種攻擊偵測 + 3 種速率超標警報
    abnormal_count = sum([
        syn_flood_detected,
        random_subdomain_detected,
        dns_amp_detected,
        tcp_rate_high,
        udp_rate_high,
        dns_rate_high
    ])
    if abnormal_count == 0:
        risk_level = "低風險"
    elif abnormal_count == 1:
        risk_level = "中風險"
    else:
        risk_level = "高風險"

    print(f"風險等級：{risk_level}")
    print("=" * 65)

if __name__ == "__main__":
    # 預設分析路徑 (預設使用隨機子網域攻擊封包進行測試)
    target_path = r"C:\Users\劉柏辰\Documents\基於封包偵測資訊安全專題\SubnetErrorAttack.pcap"
    
    # 支援透過命令列引數傳入其他 pcap 檔路徑
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        
    analyze_pcap(target_path)
