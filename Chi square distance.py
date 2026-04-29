import cv2
import os
import numpy as np

def compute_chi_square_cost(hist1, hist2):
    """
    實作 Chi-square distance 公式
    """
    eps = 1e-10
    return 0.5 * np.sum(((hist1 - hist2) ** 2) / (hist1 + hist2 + eps))

def get_shape_context(points, r_bins=5, theta_bins=12):
    """
    計算形狀脈絡直方圖 h_i(k)
    建立對數極座標空間的 bin (預設 5 個半徑區間、12 個角度區間)
    """
    n_points = len(points)
    # 直方圖長度 K = r_bins * theta_bins
    histograms = np.zeros((n_points, r_bins * theta_bins))
    
    for i in range(n_points):
        # 計算相對於點 i 的所有其他點的向量
        diffs = points - points[i]
        diffs = np.delete(diffs, i, axis=0) # 排除自身
        
        distances = np.linalg.norm(diffs, axis=1)
        angles = np.arctan2(diffs[:, 1], diffs[:, 0])
        
        # 距離正規化與對數轉換 (log r)
        mean_dist = np.mean(distances)
        if mean_dist > 0:
            distances = distances / mean_dist
        log_distances = np.log10(distances + 1e-5)
        
        # 劃分至對應的 bin
        r_edges = np.linspace(log_distances.min(), log_distances.max(), r_bins + 1)
        t_edges = np.linspace(-np.pi, np.pi, theta_bins + 1)
        
        r_idx = np.digitize(log_distances, r_edges) - 1
        theta_idx = np.digitize(angles, t_edges) - 1
        
        # 修正邊界值
        r_idx = np.clip(r_idx, 0, r_bins - 1)
        theta_idx = np.clip(theta_idx, 0, theta_bins - 1)
        
        # 統計各 bin 內的點數 (投票)
        for r, t in zip(r_idx, theta_idx):
            histograms[i, r * theta_bins + t] += 1
            
    return histograms

def detect_and_draw_objects(image_path, output_path):
    if not os.path.exists(image_path):
        print(f"找不到圖片：{image_path}")
        return

    print(f"正在分析圖片：{image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("圖片讀取失敗。")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    blurred = cv2.bilateralFilter(enhanced, 5, 75, 75)
    
    median_val = np.median(blurred)
    lower_thresh = int(max(0, (1.0 - 0.33) * median_val))
    upper_thresh = int(min(255, (1.0 + 0.33) * median_val))
    edges = cv2.Canny(blurred, lower_thresh, upper_thresh)

    kernel = np.ones((3, 3), np.uint8)
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result_img = np.zeros_like(gray)

    # 過濾面積並繪製黑底白邊目標
    valid_contours = [c for c in contours if cv2.contourArea(c) > 100]
    
    count = len(valid_contours)
    for contour in valid_contours:
        cv2.drawContours(result_img, [contour], -1, 255, -1)
        
    print(f"掃描完成！共標記了 {count} 個主要區塊。")
    cv2.imwrite(output_path, result_img)
    print(f"結果已儲存為新圖片：{output_path}")

    # ==========================================
    # 整合 Chi-square Shape Context 比較邏輯
    # ==========================================
    # 若存在兩個以上的輪廓，則對最大的兩個輪廓計算 C_ij 成本矩陣
    if len(valid_contours) >= 2:
        valid_contours = sorted(valid_contours, key=cv2.contourArea, reverse=True)
        
        # 均勻採樣 N 個點以降低計算維度
        N = 50 
        pts1 = valid_contours[0][:, 0, :]
        pts2 = valid_contours[1][:, 0, :]
        
        idx1 = np.linspace(0, len(pts1)-1, N, dtype=int)
        idx2 = np.linspace(0, len(pts2)-1, N, dtype=int)
        
        sampled_pts1 = pts1[idx1]
        sampled_pts2 = pts2[idx2]
        
        # 計算特徵直方圖 h_i 與 h_j
        print("正在計算 Shape Context 直方圖...")
        hist1 = get_shape_context(sampled_pts1)
        hist2 = get_shape_context(sampled_pts2)
        
        # 建立成本矩陣 C_ij
        cost_matrix = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                cost_matrix[i, j] = compute_chi_square_cost(hist1[i], hist2[j])
        
        print(f"Chi-square 距離掃描分析完成。")
        print(f"已產生成本矩陣大小: {cost_matrix.shape}，可用於後續最小成本分派演算法 (如 Hungarian algorithm)。")

if __name__ == "__main__":
    input_img = r'C:\Users\user\Pictures\Saved Pictures\getImage.jpg'
    output_img = r'C:\Users\user\Pictures\Saved Pictures\detected_getImage.jpg'
    detect_and_draw_objects(input_img, output_img)