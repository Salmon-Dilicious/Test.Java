import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.List;

public class PacketAnalyzerGUI extends JFrame {

    private JTextField txtFilePath;
    private JButton btnChoose;
    private JButton btnAnalyze;

    // 統計數據標籤
    private JLabel lblTCPCount;
    private JLabel lblUDPCount;
    private JLabel lblDNSCount;

    // 偵測威脅標籤
    private JLabel lblSynFlood;
    private JLabel lblNXDomain;
    private JLabel lblDNSAmp;

    // 封包接收速率顯示標籤（統計面板）
    private JLabel lblTCPRate;
    private JLabel lblUDPRate;
    private JLabel lblDNSRate;

    // 封包速率警報標籤（威脅面板）
    private JLabel lblTCPRateAlert;
    private JLabel lblUDPRateAlert;
    private JLabel lblDNSRateAlert;

    // 風險評估面板與文字
    private JPanel riskPanel;
    private JLabel lblRiskTitle;
    private JLabel lblRiskStatus;
    private JLabel lblRiskDesc;

    // 終端機控制台
    private JTextArea txtConsole;

    // Python 核心分析程式的預設路徑 (相對於專案目錄)
    private static final String PYTHON_SCRIPT_NAME = "Python/WireShark.py";

    // 取得 Java class 檔案實際所在的目錄，並向上搜尋以對齊包含 Python/WireShark.py 的專案根目錄 (解決 VS Code 將 class 編譯在 bin/ 子目錄的問題)
    private static File getProjectBaseDir() {
        // 已知專案目錄的硬編碼路徑（最高優先備用）
        String[] hardcodedPaths = {
            System.getProperty("user.home") + "\\Documents\\基於封包偵測資訊安全專題",
            "C:\\Users\\劉柏辰\\Documents\\基於封包偵測資訊安全專題"
        };
        
        // 首先檢查硬編碼路徑
        for (String hp : hardcodedPaths) {
            File hpDir = new File(hp);
            if (hpDir.exists() && new File(hpDir, PYTHON_SCRIPT_NAME).exists()) {
                return hpDir;
            }
        }

        try {
            File codeSourceFile = new File(PacketAnalyzerGUI.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            File baseDir = codeSourceFile.isFile() ? codeSourceFile.getParentFile() : codeSourceFile;
            
            // 從 class 所在目錄往上層搜尋至多 5 層
            File checkDir = baseDir;
            for (int i = 0; i < 5; i++) {
                if (checkDir == null) break;
                File targetScript = new File(checkDir, PYTHON_SCRIPT_NAME);
                if (targetScript.exists()) {
                    return checkDir;
                }
                checkDir = checkDir.getParentFile();
            }
            
            // 備用：使用目前工作目錄
            File workDir = new File(System.getProperty("user.dir"));
            if (new File(workDir, PYTHON_SCRIPT_NAME).exists()) {
                return workDir;
            }
            
            return baseDir;
        } catch (Exception e) {
            // 備用方案：使用目前工作目錄
            return new File(System.getProperty("user.dir"));
        }
    }

    public PacketAnalyzerGUI() {
        // 設定 Swing Look and Feel 為系統原生樣式
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        setTitle("基於封包偵測之資訊安全專題 - 封包安全分析系統");
        setSize(1050, 820);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null); // 居中顯示

        // 初始化佈局與元件
        initUI();
    }

    private void initUI() {
        // 主容器設定
        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(15, 15, 15, 15));
        setContentPane(mainPanel);

        // ==================== 1. 北部面板 (標題與檔案選擇) ====================
        JPanel northPanel = new JPanel(new BorderLayout(5, 10));
        
        // 系統標題
        JLabel lblTitle = new JLabel("基於封包偵測之網路安全防護偵測系統", JLabel.CENTER);
        lblTitle.setFont(new Font("Microsoft JhengHei", Font.BOLD, 22));
        lblTitle.setBorder(new EmptyBorder(0, 0, 10, 0));
        northPanel.add(lblTitle, BorderLayout.NORTH);

        // 檔案選擇列 Panel
        JPanel fileChooserPanel = new JPanel(new BorderLayout(8, 0));
        fileChooserPanel.setBorder(BorderFactory.createTitledBorder("封包檔案載入區 (pcap / pcapng)"));
        
        txtFilePath = new JTextField();
        txtFilePath.setEditable(false);
        txtFilePath.setFont(new Font("Consolas", Font.PLAIN, 12));
        txtFilePath.setBackground(new Color(245, 245, 245));
        fileChooserPanel.add(txtFilePath, BorderLayout.CENTER);

        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 5, 0));
        btnChoose = new JButton("選擇檔案");
        btnChoose.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        btnChoose.addActionListener(new ChooseFileAction());
        
        btnAnalyze = new JButton("開始分析");
        btnAnalyze.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        btnAnalyze.setEnabled(false); // 必須先選擇檔案才能分析
        btnAnalyze.addActionListener(new RunAnalysisAction());

        buttonPanel.add(btnChoose);
        buttonPanel.add(btnAnalyze);
        fileChooserPanel.add(buttonPanel, BorderLayout.EAST);

        northPanel.add(fileChooserPanel, BorderLayout.CENTER);
        mainPanel.add(northPanel, BorderLayout.NORTH);

        // ==================== 2. 中部面板 (統計、威脅與風險指標) ====================
        JPanel centerPanel = new JPanel(new GridLayout(1, 2, 10, 0));

        // --- 左側面板：指標統計與偵測判定 (Grid 2x1) ---
        JPanel leftMetricsPanel = new JPanel(new GridLayout(2, 1, 0, 10));

        // 協定統計面板
        JPanel statsPanel = new JPanel(new GridBagLayout());
        statsPanel.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createEtchedBorder(), "網路協定封包概覽", 
                TitledBorder.LEFT, TitledBorder.TOP, 
                new Font("Microsoft JhengHei", Font.BOLD, 13)
        ));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(3, 8, 3, 8);
        gbc.weightx = 1.0;

        // TCP
        gbc.gridx = 0; gbc.gridy = 0;
        JLabel lblTCPTitle = new JLabel("TCP 封包統計:", JLabel.LEFT);
        lblTCPTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        statsPanel.add(lblTCPTitle, gbc);
        gbc.gridx = 1;
        lblTCPCount = new JLabel("-", JLabel.RIGHT);
        lblTCPCount.setFont(new Font("Consolas", Font.BOLD, 13));
        statsPanel.add(lblTCPCount, gbc);

        // UDP
        gbc.gridx = 0; gbc.gridy = 1;
        JLabel lblUDPTitle = new JLabel("UDP 封包統計:", JLabel.LEFT);
        lblUDPTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        statsPanel.add(lblUDPTitle, gbc);
        gbc.gridx = 1;
        lblUDPCount = new JLabel("-", JLabel.RIGHT);
        lblUDPCount.setFont(new Font("Consolas", Font.BOLD, 13));
        statsPanel.add(lblUDPCount, gbc);

        // DNS
        gbc.gridx = 0; gbc.gridy = 2;
        JLabel lblDNSTitle = new JLabel("DNS 封包統計:", JLabel.LEFT);
        lblDNSTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        statsPanel.add(lblDNSTitle, gbc);
        gbc.gridx = 1;
        lblDNSCount = new JLabel("-", JLabel.RIGHT);
        lblDNSCount.setFont(new Font("Consolas", Font.BOLD, 13));
        statsPanel.add(lblDNSCount, gbc);

        // 分隔線標題
        gbc.gridx = 0; gbc.gridy = 3; gbc.gridwidth = 2;
        gbc.insets = new Insets(1, 8, 1, 8);
        JLabel lblRateSeparator = new JLabel("── 接收速率 (pps) ──", JLabel.CENTER);
        lblRateSeparator.setFont(new Font("Microsoft JhengHei", Font.ITALIC, 11));
        lblRateSeparator.setForeground(Color.GRAY);
        statsPanel.add(lblRateSeparator, gbc);
        gbc.gridwidth = 1;
        gbc.insets = new Insets(3, 8, 3, 8);

        // TCP 接收速率
        gbc.gridx = 0; gbc.gridy = 4;
        JLabel lblTCPRateTitle = new JLabel("TCP 接收速率:", JLabel.LEFT);
        lblTCPRateTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        statsPanel.add(lblTCPRateTitle, gbc);
        gbc.gridx = 1;
        lblTCPRate = new JLabel("-", JLabel.RIGHT);
        lblTCPRate.setFont(new Font("Consolas", Font.BOLD, 12));
        statsPanel.add(lblTCPRate, gbc);

        // UDP 接收速率
        gbc.gridx = 0; gbc.gridy = 5;
        JLabel lblUDPRateTitle = new JLabel("UDP 接收速率:", JLabel.LEFT);
        lblUDPRateTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        statsPanel.add(lblUDPRateTitle, gbc);
        gbc.gridx = 1;
        lblUDPRate = new JLabel("-", JLabel.RIGHT);
        lblUDPRate.setFont(new Font("Consolas", Font.BOLD, 12));
        statsPanel.add(lblUDPRate, gbc);

        // DNS 接收速率
        gbc.gridx = 0; gbc.gridy = 6;
        JLabel lblDNSRateTitle = new JLabel("DNS 接收速率:", JLabel.LEFT);
        lblDNSRateTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        statsPanel.add(lblDNSRateTitle, gbc);
        gbc.gridx = 1;
        lblDNSRate = new JLabel("-", JLabel.RIGHT);
        lblDNSRate.setFont(new Font("Consolas", Font.BOLD, 12));
        statsPanel.add(lblDNSRate, gbc);

        leftMetricsPanel.add(statsPanel);

        // 威脅判定面板
        JPanel threatPanel = new JPanel(new GridBagLayout());
        threatPanel.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createEtchedBorder(), "威脅檢測引擎狀態", 
                TitledBorder.LEFT, TitledBorder.TOP, 
                new Font("Microsoft JhengHei", Font.BOLD, 13)
        ));

        // SYN Flood
        gbc.gridx = 0; gbc.gridy = 0;
        JLabel lblSynTitle = new JLabel("TCP SYN Flood 偵測:", JLabel.LEFT);
        lblSynTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        threatPanel.add(lblSynTitle, gbc);
        gbc.gridx = 1;
        lblSynFlood = new JLabel("待檢測", JLabel.RIGHT);
        lblSynFlood.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        lblSynFlood.setForeground(Color.GRAY);
        threatPanel.add(lblSynFlood, gbc);

        // Random Subdomain
        gbc.gridx = 0; gbc.gridy = 1;
        JLabel lblSubnetTitle = new JLabel("DNS 隨機子網域攻擊:", JLabel.LEFT);
        lblSubnetTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        threatPanel.add(lblSubnetTitle, gbc);
        gbc.gridx = 1;
        lblNXDomain = new JLabel("待檢測", JLabel.RIGHT);
        lblNXDomain.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        lblNXDomain.setForeground(Color.GRAY);
        threatPanel.add(lblNXDomain, gbc);

        // DNS Amplification
        gbc.gridx = 0; gbc.gridy = 2;
        JLabel lblAmpTitle = new JLabel("DNS 放大反射攻擊:", JLabel.LEFT);
        lblAmpTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        threatPanel.add(lblAmpTitle, gbc);
        gbc.gridx = 1;
        lblDNSAmp = new JLabel("待檢測", JLabel.RIGHT);
        lblDNSAmp.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        lblDNSAmp.setForeground(Color.GRAY);
        threatPanel.add(lblDNSAmp, gbc);

        // 分隔線
        gbc.gridx = 0; gbc.gridy = 3; gbc.gridwidth = 2;
        gbc.insets = new Insets(1, 8, 1, 8);
        JLabel lblRateAlertSep = new JLabel("── 速率警報 (>10K PPS) ──", JLabel.CENTER);
        lblRateAlertSep.setFont(new Font("Microsoft JhengHei", Font.ITALIC, 11));
        lblRateAlertSep.setForeground(Color.GRAY);
        threatPanel.add(lblRateAlertSep, gbc);
        gbc.gridwidth = 1;
        gbc.insets = new Insets(3, 8, 3, 8);

        // TCP 速率警報
        gbc.gridx = 0; gbc.gridy = 4;
        JLabel lblTCPRateAlertTitle = new JLabel("TCP 速率警報:", JLabel.LEFT);
        lblTCPRateAlertTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        threatPanel.add(lblTCPRateAlertTitle, gbc);
        gbc.gridx = 1;
        lblTCPRateAlert = new JLabel("待檢測", JLabel.RIGHT);
        lblTCPRateAlert.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        lblTCPRateAlert.setForeground(Color.GRAY);
        threatPanel.add(lblTCPRateAlert, gbc);

        // UDP 速率警報
        gbc.gridx = 0; gbc.gridy = 5;
        JLabel lblUDPRateAlertTitle = new JLabel("UDP 速率警報:", JLabel.LEFT);
        lblUDPRateAlertTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        threatPanel.add(lblUDPRateAlertTitle, gbc);
        gbc.gridx = 1;
        lblUDPRateAlert = new JLabel("待檢測", JLabel.RIGHT);
        lblUDPRateAlert.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        lblUDPRateAlert.setForeground(Color.GRAY);
        threatPanel.add(lblUDPRateAlert, gbc);

        // DNS 速率警報
        gbc.gridx = 0; gbc.gridy = 6;
        JLabel lblDNSRateAlertTitle = new JLabel("DNS 速率警報:", JLabel.LEFT);
        lblDNSRateAlertTitle.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        threatPanel.add(lblDNSRateAlertTitle, gbc);
        gbc.gridx = 1;
        lblDNSRateAlert = new JLabel("待檢測", JLabel.RIGHT);
        lblDNSRateAlert.setFont(new Font("Microsoft JhengHei", Font.BOLD, 12));
        lblDNSRateAlert.setForeground(Color.GRAY);
        threatPanel.add(lblDNSRateAlert, gbc);

        leftMetricsPanel.add(threatPanel);
        centerPanel.add(leftMetricsPanel);

        // --- 右側面板：風險評估大字面板與即時 Console 區 (Border Layout) ---
        JPanel rightStatusPanel = new JPanel(new BorderLayout(0, 10));

        // 風險指標卡片 Panel
        riskPanel = new JPanel();
        riskPanel.setLayout(new BoxLayout(riskPanel, BoxLayout.Y_AXIS));
        riskPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(220, 220, 220), 1),
                new EmptyBorder(15, 10, 15, 10)
        ));
        riskPanel.setBackground(new Color(245, 245, 245));

        lblRiskTitle = new JLabel("NIDS 風險評估評級", JLabel.CENTER);
        lblRiskTitle.setFont(new Font("Microsoft JhengHei", Font.BOLD, 13));
        lblRiskTitle.setForeground(Color.DARK_GRAY);
        lblRiskTitle.setAlignmentX(Component.CENTER_ALIGNMENT);

        lblRiskStatus = new JLabel("待分析", JLabel.CENTER);
        lblRiskStatus.setFont(new Font("Microsoft JhengHei", Font.BOLD, 32));
        lblRiskStatus.setForeground(Color.GRAY);
        lblRiskStatus.setAlignmentX(Component.CENTER_ALIGNMENT);
        lblRiskStatus.setBorder(new EmptyBorder(5, 0, 5, 0));

        lblRiskDesc = new JLabel("請選擇 PCAP 封包檔案並點擊開始分析", JLabel.CENTER);
        lblRiskDesc.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 12));
        lblRiskDesc.setForeground(Color.GRAY);
        lblRiskDesc.setAlignmentX(Component.CENTER_ALIGNMENT);

        riskPanel.add(lblRiskTitle);
        riskPanel.add(Box.createRigidArea(new Dimension(0, 5)));
        riskPanel.add(lblRiskStatus);
        riskPanel.add(Box.createRigidArea(new Dimension(0, 5)));
        riskPanel.add(lblRiskDesc);

        rightStatusPanel.add(riskPanel, BorderLayout.NORTH);

        // 控制台輸出 Panel
        JPanel consolePanel = new JPanel(new BorderLayout());
        consolePanel.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createEtchedBorder(), "封包安全分析引擎日誌輸出", 
                TitledBorder.LEFT, TitledBorder.TOP, 
                new Font("Microsoft JhengHei", Font.BOLD, 13)
        ));

        txtConsole = new JTextArea();
        txtConsole.setEditable(false);
        txtConsole.setFont(new Font("Consolas", Font.PLAIN, 12));
        txtConsole.setBackground(new Color(30, 30, 30));
        txtConsole.setForeground(new Color(220, 220, 220));
        
        JScrollPane scrollPane = new JScrollPane(txtConsole);
        consolePanel.add(scrollPane, BorderLayout.CENTER);
        
        rightStatusPanel.add(consolePanel, BorderLayout.CENTER);

        centerPanel.add(rightStatusPanel);
        mainPanel.add(centerPanel, BorderLayout.CENTER);

        // ==================== 3. 底部版權資訊 ====================
        JLabel lblFooter = new JLabel("基於封包偵測資訊安全專題 © 2026", JLabel.CENTER);
        lblFooter.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 10));
        lblFooter.setForeground(Color.GRAY);
        mainPanel.add(lblFooter, BorderLayout.SOUTH);
    }

    // 處理選擇檔案按鈕點擊
    private class ChooseFileAction implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            JFileChooser fileChooser = new JFileChooser();
            // 預設為 Java 程式碼實際所在的專案目錄
            fileChooser.setCurrentDirectory(getProjectBaseDir());
            fileChooser.setFileSelectionMode(JFileChooser.FILES_ONLY);
            // 篩選 pcap/pcapng
            fileChooser.setFileFilter(new javax.swing.filechooser.FileFilter() {
                @Override
                public boolean accept(File f) {
                    if (f.isDirectory()) return true;
                    String name = f.getName().toLowerCase();
                    return name.endsWith(".pcap") || name.endsWith(".pcapng");
                }

                @Override
                public String getDescription() {
                    return "Wireshark 封包擷取檔案 (*.pcap, *.pcapng)";
                }
            });

            int result = fileChooser.showOpenDialog(PacketAnalyzerGUI.this);
            if (result == JFileChooser.APPROVE_OPTION) {
                File selectedFile = fileChooser.getSelectedFile();
                txtFilePath.setText(selectedFile.getAbsolutePath());
                btnAnalyze.setEnabled(true); // 啟用分析按鈕
                resetGUIResults(); // 重置上一次的分析顯示
            }
        }
    }

    // 重置所有介面統計指標
    private void resetGUIResults() {
        lblTCPCount.setText("-");
        lblUDPCount.setText("-");
        lblDNSCount.setText("-");
        lblTCPRate.setText("-");
        lblUDPRate.setText("-");
        lblDNSRate.setText("-");
        lblSynFlood.setText("待檢測");
        lblSynFlood.setForeground(Color.GRAY);
        lblNXDomain.setText("待檢測");
        lblNXDomain.setForeground(Color.GRAY);
        lblDNSAmp.setText("待檢測");
        lblDNSAmp.setForeground(Color.GRAY);
        lblTCPRateAlert.setText("待檢測");
        lblTCPRateAlert.setForeground(Color.GRAY);
        lblUDPRateAlert.setText("待檢測");
        lblUDPRateAlert.setForeground(Color.GRAY);
        lblDNSRateAlert.setText("待檢測");
        lblDNSRateAlert.setForeground(Color.GRAY);
        
        riskPanel.setBackground(new Color(245, 245, 245));
        lblRiskStatus.setText("待分析");
        lblRiskStatus.setForeground(Color.GRAY);
        lblRiskDesc.setText("已載入封包檔案，請點擊開始分析。");
        lblRiskDesc.setForeground(Color.GRAY);
        
        txtConsole.setText("");
    }

    // 執行開始分析按鈕點擊
    private class RunAnalysisAction implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            String pcapPath = txtFilePath.getText();
            if (pcapPath == null || pcapPath.trim().isEmpty()) {
                JOptionPane.showMessageDialog(PacketAnalyzerGUI.this, "請先選擇封包檔案！", "錯誤", JOptionPane.ERROR_MESSAGE);
                return;
            }

            // 鎖定 UI 避免重複點擊
            btnChoose.setEnabled(false);
            btnAnalyze.setEnabled(false);
            lblRiskStatus.setText("分析中...");
            lblRiskStatus.setForeground(Color.BLUE);
            lblRiskDesc.setText("Python 封包安全分析引擎執行中，請稍候...");
            txtConsole.setText("--- 開始分析封包檔案 ---\n路徑: " + pcapPath + "\n\n");

            // 使用 SwingWorker 背景執行，防止介面凍結
            new AnalysisWorker(pcapPath).execute();
        }
    }

    // SwingWorker 背景進程，整合 ProcessBuilder 處理核心分析與 stdout 串流解析
    private class AnalysisWorker extends SwingWorker<Void, String> {
        private String pcapPath;
        private boolean isSynFloodAlert = false;
        private boolean isNXDomainAlert = false;
        private boolean isDNSAmpAlert = false;
        private boolean isTCPRateHigh = false;
        private boolean isUDPRateHigh = false;
        private boolean isDNSRateHigh = false;
        private String tcpRateDisplay = "-";
        private String udpRateDisplay = "-";
        private String dnsRateDisplay = "-";
        private String riskLevelResult = "低風險";

        public AnalysisWorker(String pcapPath) {
            this.pcapPath = pcapPath;
        }

        @Override
        protected Void doInBackground() throws Exception {
            // 尋找 Python 核心分析程式 (基於 Java class 的絕對路徑動態對齊)
            File projectDir = getProjectBaseDir();
            File scriptFile = new File(projectDir, PYTHON_SCRIPT_NAME);
            String scriptPath = scriptFile.getAbsolutePath();

            if (!scriptFile.exists()) {
                publish("[-] 錯誤：找不到 Python 分析核心模組 " + PYTHON_SCRIPT_NAME + "\n");
                publish("[-] 系統預期路徑為: " + scriptPath + "\n");
                return null;
            }

            // 支援的 Python 指令清單與備用絕對路徑 (防範環境變數未設定時啟動失敗)
            String[] pythonCommands = {
                "python",
                "py",
                System.getProperty("user.home") + "\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
                System.getProperty("user.home") + "\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
                System.getProperty("user.home") + "\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
                System.getProperty("user.home") + "\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
                "python3"
            };

            Process process = null;
            Exception lastException = null;

            for (String pythonCmd : pythonCommands) {
                try {
                    publish("[*] 嘗試使用指令 [" + pythonCmd + "] 啟動... ");
                    ProcessBuilder pb = new ProcessBuilder(pythonCmd, scriptPath, pcapPath);
                    // 設定子進程工作目錄為專案根目錄，確保 Python 能正常解析相對檔案路徑
                    pb.directory(projectDir);
                    // 強制 Python 以 UTF-8 輸出編碼，防止 Windows 本地 CP950/UTF-8 字符判定失敗
                    pb.environment().put("PYTHONIOENCODING", "UTF-8");
                    pb.redirectErrorStream(true); // 合併 stderr 與 stdout
                    process = pb.start();
                    publish("啟動成功！\n[+] 正在解析封包檔，請稍候...\n\n");
                    break; 
                } catch (Exception e) {
                    lastException = e;
                    publish("失敗\n");
                }
            }

            if (process == null) {
                publish("[-] 錯誤：無法啟動 Python 分析引擎。\n");
                if (lastException != null) {
                    publish("[-] 系統回傳訊息: " + lastException.getMessage() + "\n");
                }
                publish("[-] 請確認您的電腦是否已安裝 Python 且 'python' 已加入 Windows 環境變數中。\n");
                return null;
            }

            // 使用 UTF-8 解碼器讀取 Python 輸出流，確保中文字元 100% 吻合
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    publish(line);

                    // 1. 解析協定統計個數 (如 "- TCP 封包數 : 102 (6.16%)")
                    if (line.contains("- TCP 封包數")) {
                        updateLabelValue(lblTCPCount, line);
                    } else if (line.contains("- UDP 封包數")) {
                        updateLabelValue(lblUDPCount, line);
                    } else if (line.contains("- DNS 封包數")) {
                        updateLabelValue(lblDNSCount, line);
                    }
                    
                    // 2. 解析威脅警告狀態
                    if (line.contains("[!] [警告] 檢測到潛在的 SYN FLOOD")) {
                        isSynFloodAlert = true;
                    } else if (line.contains("[OK] [正常] TCP 安全評估通過")) {
                        isSynFloodAlert = false;
                    }
                    
                    if (line.contains("[!] [警告] 疑似遭受隨機子網域攻擊")) {
                        isNXDomainAlert = true;
                    } else if (line.contains("[OK] [正常] 隨機子網域分析評估通過")) {
                        isNXDomainAlert = false;
                    }
                    
                    if (line.contains("[!] [警告] 疑似遭受 DNS 放大攻擊")) {
                        isDNSAmpAlert = true;
                    } else if (line.contains("[OK] [正常] DNS 放大攻擊分析通過")) {
                        isDNSAmpAlert = false;
                    }

                    // 3. 解析封包接收速率數值
                    if (line.contains("- TCP 封包接收速率")) {
                        tcpRateDisplay = line.substring(line.indexOf(":") + 1).trim();
                    } else if (line.contains("- UDP 封包接收速率")) {
                        udpRateDisplay = line.substring(line.indexOf(":") + 1).trim();
                    } else if (line.contains("- DNS 封包接收速率")) {
                        dnsRateDisplay = line.substring(line.indexOf(":") + 1).trim();
                    }

                    // 4. 解析速率警報狀態
                    if (line.contains("[!] [警告] TCP 封包速率超過門檻")) {
                        isTCPRateHigh = true;
                    } else if (line.contains("[OK] [正常] TCP 封包速率正常")) {
                        isTCPRateHigh = false;
                    }
                    if (line.contains("[!] [警告] UDP 封包速率超過門檻")) {
                        isUDPRateHigh = true;
                    } else if (line.contains("[OK] [正常] UDP 封包速率正常")) {
                        isUDPRateHigh = false;
                    }
                    if (line.contains("[!] [警告] DNS 封包速率超過門檻")) {
                        isDNSRateHigh = true;
                    } else if (line.contains("[OK] [正常] DNS 封包速率正常")) {
                        isDNSRateHigh = false;
                    }

                    // 5. 解析風險等級 (最後一行字串，例如 "風險等級：中風險")
                    if (line.contains("風險等級：")) {
                        riskLevelResult = line.substring(line.indexOf("風險等級：") + 5).trim();
                    }
                }
            } catch (Exception e) {
                publish("[-] 讀取分析結果時發生錯誤: " + e.getMessage() + "\n");
            }

            try {
                process.waitFor();
            } catch (Exception e) {
                // 忽略等待例外
            }
            return null;
        }

        // 輔助函式：從輸出中擷取 ":" 後面的統計數據 (去除百分比括號部分)
        private void updateLabelValue(JLabel label, String line) {
            if (line.contains(":")) {
                String value = line.substring(line.indexOf(":") + 1).trim();
                // 去掉百分比部分（括號及之後的內容）
                if (value.contains("(")) {
                    value = value.substring(0, value.indexOf("(")).trim();
                }
                label.setText(value);
            }
        }

        @Override
        protected void process(List<String> chunks) {
            // 在主線程更新 Console 區域
            for (String line : chunks) {
                txtConsole.append(line + "\n");
                // 自動滾動到日誌最底端
                txtConsole.setCaretPosition(txtConsole.getDocument().getLength());
            }
        }

        @Override
        protected void done() {
            // 還原控制按鈕狀態
            btnChoose.setEnabled(true);
            btnAnalyze.setEnabled(true);

            // 1. 更新威脅引擎狀態標籤（含速率警報）
            updateThreatLabel(lblSynFlood, isSynFloodAlert);
            updateThreatLabel(lblNXDomain, isNXDomainAlert);
            updateThreatLabel(lblDNSAmp, isDNSAmpAlert);
            updateRateAlertLabel(lblTCPRateAlert, isTCPRateHigh, tcpRateDisplay);
            updateRateAlertLabel(lblUDPRateAlert, isUDPRateHigh, udpRateDisplay);
            updateRateAlertLabel(lblDNSRateAlert, isDNSRateHigh, dnsRateDisplay);

            // 更新速率數值顯示
            lblTCPRate.setText(tcpRateDisplay);
            lblUDPRate.setText(udpRateDisplay);
            lblDNSRate.setText(dnsRateDisplay);

            // 2. 動態渲染風險卡片顏色
            if ("低風險".equals(riskLevelResult)) {
                riskPanel.setBackground(new Color(46, 204, 113)); // 綠色
                lblRiskTitle.setForeground(Color.WHITE);
                lblRiskStatus.setText("低風險");
                lblRiskStatus.setForeground(Color.WHITE);
                lblRiskDesc.setText("安全狀況良好，未發現異常活動特徵。");
                lblRiskDesc.setForeground(Color.WHITE);
            } else if ("中風險".equals(riskLevelResult)) {
                riskPanel.setBackground(new Color(230, 126, 34)); // 橘黃色
                lblRiskTitle.setForeground(Color.WHITE);
                lblRiskStatus.setText("中風險");
                lblRiskStatus.setForeground(Color.WHITE);
                lblRiskDesc.setText("發現 1 項安全威脅異常，請注意防護。");
                lblRiskDesc.setForeground(Color.WHITE);
            } else if ("高風險".equals(riskLevelResult)) {
                riskPanel.setBackground(new Color(231, 76, 60)); // 紅色
                lblRiskTitle.setForeground(Color.WHITE);
                lblRiskStatus.setText("高風險");
                lblRiskStatus.setForeground(Color.WHITE);
                lblRiskDesc.setText("發現 2 項以上嚴重安全異常，可能遭受侵入攻擊！");
                lblRiskDesc.setForeground(Color.WHITE);
            } else {
                riskPanel.setBackground(new Color(245, 245, 245));
                lblRiskTitle.setForeground(Color.DARK_GRAY);
                lblRiskStatus.setText(riskLevelResult);
                lblRiskStatus.setForeground(Color.GRAY);
                lblRiskDesc.setText("分析完成。");
                lblRiskDesc.setForeground(Color.GRAY);
            }
            
            txtConsole.append("\n--- 分析結束 ---");
        }

        // 輔助更新偵測狀態標籤色彩與符號
        private void updateThreatLabel(JLabel label, boolean isAlert) {
            if (isAlert) {
                label.setText("⚠️ 異常 (偵測到攻擊)");
                label.setForeground(new Color(231, 76, 60)); // 紅色
            } else {
                label.setText("✅ 正常");
                label.setForeground(new Color(46, 204, 113)); // 綠色
            }
        }

        // 輔助更新速率警報標籤（顯示實際速率值）
        private void updateRateAlertLabel(JLabel label, boolean isHigh, String rateVal) {
            if (isHigh) {
                label.setText("⚠️ 超速！(" + rateVal + ")");
                label.setForeground(new Color(231, 76, 60)); // 紅色
            } else {
                label.setText("✅ 正常 (" + rateVal + ")");
                label.setForeground(new Color(46, 204, 113)); // 綠色
            }
        }
    }

    public static void main(String[] args) {
        // 強制設定工作目錄為專案根目錄，避免 VS Code 從錯誤路徑啟動導致找不到 Python 腳本
        String projectDir = System.getProperty("user.home") + "\\Documents\\基於封包偵測資訊安全專題";
        File projFile = new File(projectDir);
        if (projFile.exists()) {
            System.setProperty("user.dir", projectDir);
        }
        
        // 在 Event Dispatch Thread 中啟動 Swing 程式，確保執行緒安全
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                PacketAnalyzerGUI gui = new PacketAnalyzerGUI();
                gui.setVisible(true);
            }
        });
    }
}
