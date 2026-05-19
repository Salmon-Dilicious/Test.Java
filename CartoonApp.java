import java.awt.*;
import java.awt.event.*;
import java.awt.image.*;
import java.io.*;
import javax.imageio.*;
import javax.swing.*;
import javax.swing.filechooser.*;

// ============================================================
//  ImageLoader — 負責從路徑讀取圖片
// ============================================================
class ImageLoader {
    /**
     * 嘗試從指定路徑載入圖片。
     * 若路徑本身不含副檔名，會自動嘗試常見圖片格式。
     */
    public BufferedImage load(String path) throws IOException {
        File file = new File(path);
        if (file.exists() && file.isFile()) {
            BufferedImage img = ImageIO.read(file);
            if (img == null) throw new IOException("無法解析圖片格式：" + path);
            return img;
        }
        // 自動補副檔名
        String[] exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"};
        for (String ext : exts) {
            File candidate = new File(path + ext);
            if (candidate.exists()) {
                BufferedImage img = ImageIO.read(candidate);
                if (img != null) return img;
            }
        }
        throw new IOException("找不到圖片檔案，已嘗試常見副檔名：" + path);
    }
}

// ============================================================
//  GaussianBlur — 高斯模糊（兩次一維卷積，效能較佳）
// ============================================================
class GaussianBlur {
    private final int radius;

    public GaussianBlur(int radius) {
        this.radius = radius;
    }

    public BufferedImage apply(BufferedImage src) {
        double[] kernel = buildKernel(radius);
        int w = src.getWidth(), h = src.getHeight();

        // 第一次：水平方向
        int[][] rH = new int[h][w], gH = new int[h][w], bH = new int[h][w];
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                double r = 0, g = 0, b = 0;
                for (int k = -radius; k <= radius; k++) {
                    int xi = clamp(x + k, 0, w - 1);
                    int rgb = src.getRGB(xi, y);
                    double wt = kernel[k + radius];
                    r += ((rgb >> 16) & 0xFF) * wt;
                    g += ((rgb >> 8) & 0xFF) * wt;
                    b += (rgb & 0xFF) * wt;
                }
                rH[y][x] = (int) r; gH[y][x] = (int) g; bH[y][x] = (int) b;
            }
        }

        // 第二次：垂直方向
        BufferedImage out = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                double r = 0, g = 0, b = 0;
                for (int k = -radius; k <= radius; k++) {
                    int yi = clamp(y + k, 0, h - 1);
                    double wt = kernel[k + radius];
                    r += rH[yi][x] * wt;
                    g += gH[yi][x] * wt;
                    b += bH[yi][x] * wt;
                }
                out.setRGB(x, y, ((int) r << 16) | ((int) g << 8) | (int) b);
            }
        }
        return out;
    }

    private double[] buildKernel(int r) {
        double sigma = Math.max(r / 2.0, 0.5);
        double[] k = new double[2 * r + 1];
        double sum = 0;
        for (int i = 0; i <= 2 * r; i++) {
            int x = i - r;
            k[i] = Math.exp(-(x * x) / (2 * sigma * sigma));
            sum += k[i];
        }
        for (int i = 0; i <= 2 * r; i++) k[i] /= sum;
        return k;
    }

    private int clamp(int v, int lo, int hi) {
        return Math.max(lo, Math.min(hi, v));
    }
}

// ============================================================
//  GrayConverter — 轉灰階
// ============================================================
class GrayConverter {
    public int[][] toGray(BufferedImage src) {
        int w = src.getWidth(), h = src.getHeight();
        int[][] gray = new int[h][w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int rgb = src.getRGB(x, y);
                int r = (rgb >> 16) & 0xFF, g = (rgb >> 8) & 0xFF, b = rgb & 0xFF;
                gray[y][x] = (int) (0.299 * r + 0.587 * g + 0.114 * b);
            }
        return gray;
    }
}

// ============================================================
//  EdgeDetector — Sobel 邊緣偵測
// ============================================================
// ============================================================
//  EdgeDetector — Sobel 邊緣偵測與自適應閾值處理
// ============================================================
class EdgeDetector {
    private int windowSize; // 局部計算的視窗大小 (必須為奇數，例如 5, 7, 9)
    private int offset;     // 閾值偏移量 (用於過濾雜訊)

    public EdgeDetector(int windowSize, int offset) {
        this.windowSize = windowSize;
        this.offset = offset;
    }

    public void setOffset(int offset) { 
        this.offset = offset; 
    }

    public boolean[][] detect(int[][] gray) {
        int h = gray.length;
        int w = gray[0].length;
        double[][] magnitudes = new double[h][w];
        boolean[][] edges = new boolean[h][w];

        int[] kx = {-1, 0, 1, -2, 0, 2, -1, 0, 1};
        int[] ky = {-1, -2, -1, 0, 0, 0, 1, 2, 1};

        // 階段一：計算全域 Sobel 梯度大小
        for (int y = 1; y < h - 1; y++) {
            for (int x = 1; x < w - 1; x++) {
                int gx = 0, gy = 0, idx = 0;
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++, idx++) {
                        int p = gray[y + dy][x + dx];
                        gx += p * kx[idx];
                        gy += p * ky[idx];
                    }
                }
                magnitudes[y][x] = Math.sqrt((double) gx * gx + (double) gy * gy);
            }
        }

        // 階段二：局部自適應閾值處理 (Local Adaptive Thresholding)
        int radius = windowSize / 2;
        for (int y = radius; y < h - radius; y++) {
            for (int x = radius; x < w - radius; x++) {
                double localSum = 0;
                int count = 0;

                // 計算局部視窗內的平均梯度值
                for (int wy = -radius; wy <= radius; wy++) {
                    for (int wx = -radius; wx <= radius; wx++) {
                        localSum += magnitudes[y + wy][x + wx];
                        count++;
                    }
                }
                double localMean = localSum / count;

                // 若該點梯度大於 (局部平均值 + 偏移量)，則判定為邊緣
                edges[y][x] = magnitudes[y][x] > (localMean + offset);
            }
        }
        return edges;
    }
}

// ============================================================
//  ColorQuantizer — 色彩量化（減少顏色層次，產生卡通平塗效果）
// ============================================================
class ColorQuantizer {
    private int levels;

    public ColorQuantizer(int levels) {
        this.levels = levels;
    }

    public void setLevels(int l) { this.levels = l; }

    public BufferedImage quantize(BufferedImage src) {
        int w = src.getWidth(), h = src.getHeight();
        BufferedImage out = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        int step = 256 / levels;
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int rgb = src.getRGB(x, y);
                int r = quantChannel((rgb >> 16) & 0xFF, step);
                int g = quantChannel((rgb >> 8) & 0xFF, step);
                int b = quantChannel(rgb & 0xFF, step);
                out.setRGB(x, y, (r << 16) | (g << 8) | b);
            }
        return out;
    }

    private int quantChannel(int v, int step) {
        return Math.min(((v / step) * step) + step / 2, 255);
    }
}

// ============================================================
//  CartoonRenderer — 將邊緣疊加到量化後的彩色圖片
// ============================================================
class CartoonRenderer {
    private Color edgeColor;

    public CartoonRenderer(Color edgeColor) {
        this.edgeColor = edgeColor;
    }

    public void setEdgeColor(Color c) { this.edgeColor = c; }

    public BufferedImage render(BufferedImage quantized, boolean[][] edges) {
        int w = quantized.getWidth(), h = quantized.getHeight();
        BufferedImage out = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        int edgeRGB = edgeColor.getRGB();
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                out.setRGB(x, y,
                    (y < edges.length && x < edges[0].length && edges[y][x])
                        ? edgeRGB
                        : quantized.getRGB(x, y));
        return out;
    }
}

// ============================================================
//  ImageExporter — 儲存輸出圖片
// ============================================================
class ImageExporter {
    public void save(BufferedImage img, String path) throws IOException {
        File f = new File(path);
        String fmt = path.toLowerCase().endsWith(".png") ? "png" : "jpg";
        if (!ImageIO.write(img, fmt, f))
            throw new IOException("儲存失敗：不支援的格式");
    }
}

// ============================================================
//  CartoonPipeline — 組合整條處理流程
// ============================================================
class CartoonPipeline {
    private final GaussianBlur blur;
    private final GrayConverter grayConv;
    private final EdgeDetector edgeDet;
    private final ColorQuantizer quantizer;
    private final CartoonRenderer renderer;

    public CartoonPipeline(int blurRadius, int edgeThreshold, int colorLevels) {
        blur      = new GaussianBlur(blurRadius);
        grayConv  = new GrayConverter();
        edgeDet   = new EdgeDetector(5,edgeThreshold);
        quantizer = new ColorQuantizer(colorLevels);
        renderer  = new CartoonRenderer(Color.BLACK);
    }

    public void setEdgeThreshold(int t) { edgeDet.setOffset(t); }
    public void setColorLevels(int l)   { quantizer.setLevels(l); }

    public BufferedImage process(BufferedImage original) {
        BufferedImage blurred   = blur.apply(original);
        int[][]       gray      = grayConv.toGray(blurred);
        boolean[][]   edges     = edgeDet.detect(gray);
        BufferedImage quantized = quantizer.quantize(blurred);
        return renderer.render(quantized, edges);
    }
}

// ============================================================
//  ScaledImagePanel — 自動縮放顯示圖片的面板
// ============================================================
class ScaledImagePanel extends JPanel {
    private BufferedImage image;
    private String placeholder;

    public ScaledImagePanel(String placeholder) {
        this.placeholder = placeholder;
        setBackground(new Color(30, 30, 35));
        setPreferredSize(new Dimension(400, 320));
    }

    public void setImage(BufferedImage img) {
        this.image = img;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                            RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        if (image == null) {
            g2.setColor(new Color(80, 80, 90));
            g2.setFont(new Font("SansSerif", Font.PLAIN, 14));
            FontMetrics fm = g2.getFontMetrics();
            g2.drawString(placeholder,
                (getWidth() - fm.stringWidth(placeholder)) / 2,
                getHeight() / 2);
            return;
        }
        double sw = (double) getWidth() / image.getWidth();
        double sh = (double) getHeight() / image.getHeight();
        double scale = Math.min(sw, sh);
        int dw = (int) (image.getWidth() * scale);
        int dh = (int) (image.getHeight() * scale);
        int ox = (getWidth() - dw) / 2;
        int oy = (getHeight() - dh) / 2;
        g2.drawImage(image, ox, oy, dw, dh, null);
    }
}

// ============================================================
//  CartoonApp — 主程式 + Swing GUI
// ============================================================
public class CartoonApp extends JFrame {

    // ── 預設輸入路徑（不含副檔名，程式會自動偵測）
    private static final String DEFAULT_INPUT = "C:\\Users\\User\\Pictures\\abc";

    private BufferedImage originalImage;
    private BufferedImage cartoonImage;

    private final CartoonPipeline pipeline;
    private final ImageLoader     loader   = new ImageLoader();
    private final ImageExporter   exporter = new ImageExporter();

    // GUI 元件
    private final ScaledImagePanel leftPanel   = new ScaledImagePanel("原始圖片");
    private final ScaledImagePanel rightPanel  = new ScaledImagePanel("卡通風格輸出");
    private final JLabel           statusLabel = new JLabel("請選擇圖片或直接按「套用預設路徑」");

    // 參數滑桿
    private JSlider sliderEdge;
    private JSlider sliderColor;

    public CartoonApp() {
        super("Traditional Cartoon Style App  —  Java OOP Challenge");
        pipeline = new CartoonPipeline(3, 50, 8);
        buildUI();
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setVisible(true);
    }

    // ── 建構 UI ──────────────────────────────────────────────
    private void buildUI() {
        getContentPane().setBackground(new Color(22, 27, 34));
        setLayout(new BorderLayout(0, 0));

        add(buildHeader(),  BorderLayout.NORTH);
        add(buildCenter(),  BorderLayout.CENTER);
        add(buildBottom(),  BorderLayout.SOUTH);

        pack();
        setMinimumSize(new Dimension(900, 620));
    }

    private JPanel buildHeader() {
        JPanel p = new JPanel(new FlowLayout(FlowLayout.LEFT, 16, 10));
        p.setBackground(new Color(13, 17, 23));
        JLabel title = new JLabel("🎨  Cartoon Style Converter");
        title.setFont(new Font("SansSerif", Font.BOLD, 18));
        title.setForeground(new Color(210, 168, 90));
        p.add(title);
        return p;
    }

    private JPanel buildCenter() {
        JPanel images = new JPanel(new GridLayout(1, 2, 12, 0));
        images.setBackground(new Color(22, 27, 34));
        images.setBorder(BorderFactory.createEmptyBorder(12, 16, 8, 16));

        leftPanel.setBorder(BorderFactory.createLineBorder(new Color(50, 60, 75), 1));
        rightPanel.setBorder(BorderFactory.createLineBorder(new Color(50, 60, 75), 1));
        images.add(wrap("原始圖片", leftPanel));
        images.add(wrap("卡通風格", rightPanel));

        JPanel controls = buildControls();

        JPanel center = new JPanel(new BorderLayout(0, 8));
        center.setBackground(new Color(22, 27, 34));
        center.add(images,   BorderLayout.CENTER);
        center.add(controls, BorderLayout.SOUTH);
        return center;
    }

    private JPanel wrap(String title, JPanel inner) {
        JPanel p = new JPanel(new BorderLayout(0, 4));
        p.setBackground(new Color(22, 27, 34));
        JLabel lbl = new JLabel(title, SwingConstants.CENTER);
        lbl.setForeground(new Color(140, 155, 175));
        lbl.setFont(new Font("SansSerif", Font.BOLD, 13));
        p.add(lbl,   BorderLayout.NORTH);
        p.add(inner, BorderLayout.CENTER);
        return p;
    }

    private JPanel buildControls() {
        JPanel p = new JPanel(new GridBagLayout());
        p.setBackground(new Color(18, 22, 30));
        p.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(4, 8, 4, 8);
        c.fill = GridBagConstraints.HORIZONTAL;

        sliderEdge  = makeSlider(-20, 50, 10);
        sliderColor = makeSlider(2, 16, 8);

        sliderEdge.addChangeListener(e -> applyIfLoaded());
        sliderColor.addChangeListener(e -> applyIfLoaded());

        c.gridx = 0; c.gridy = 0; c.weightx = 0;
        p.add(label("邊緣閾值:"), c);
        c.gridx = 1; c.weightx = 1;
        p.add(sliderEdge, c);
        c.gridx = 2; c.weightx = 0;
        p.add(valLabel(sliderEdge, ""), c);

        c.gridx = 0; c.gridy = 1; c.weightx = 0;
        p.add(label("色彩層次:"), c);
        c.gridx = 1; c.weightx = 1;
        p.add(sliderColor, c);
        c.gridx = 2; c.weightx = 0;
        p.add(valLabel(sliderColor, " 階"), c);

        return p;
    }

    private JPanel buildBottom() {
        JPanel p = new JPanel(new FlowLayout(FlowLayout.CENTER, 12, 10));
        p.setBackground(new Color(13, 17, 23));

        p.add(btn("📂 開啟圖片",   new Color(40, 90, 160),  e -> openImage()));
        p.add(btn("⚡ 預設路徑",   new Color(60, 120, 60),  e -> loadDefault()));
        p.add(btn("💾 儲存結果",   new Color(130, 80, 20),  e -> saveResult()));

        statusLabel.setForeground(new Color(140, 155, 175));
        statusLabel.setFont(new Font("SansSerif", Font.PLAIN, 12));
        p.add(statusLabel);
        return p;
    }

    // ── 按鈕與滑桿工廠 ───────────────────────────────────────
    private JButton btn(String text, Color bg, ActionListener al) {
        JButton b = new JButton(text);
        b.setBackground(bg);
        b.setForeground(Color.WHITE);
        b.setFont(new Font("SansSerif", Font.BOLD, 13));
        b.setFocusPainted(false);
        b.setBorder(BorderFactory.createEmptyBorder(7, 18, 7, 18));
        b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        b.addActionListener(al);
        return b;
    }

    private JSlider makeSlider(int min, int max, int val) {
        JSlider s = new JSlider(min, max, val);
        s.setBackground(new Color(18, 22, 30));
        s.setForeground(new Color(210, 168, 90));
        s.setPreferredSize(new Dimension(220, 28));
        return s;
    }

    private JLabel label(String t) {
        JLabel l = new JLabel(t);
        l.setForeground(new Color(180, 190, 205));
        l.setFont(new Font("SansSerif", Font.PLAIN, 13));
        return l;
    }

    private JLabel valLabel(JSlider slider, String suffix) {
        JLabel l = new JLabel(slider.getValue() + suffix);
        l.setForeground(new Color(210, 168, 90));
        l.setFont(new Font("Monospaced", Font.BOLD, 13));
        l.setPreferredSize(new Dimension(50, 20));
        slider.addChangeListener(e -> l.setText(slider.getValue() + suffix));
        return l;
    }

    // ── 動作方法 ─────────────────────────────────────────────
    private void openImage() {
        JFileChooser fc = new JFileChooser();
        fc.setFileFilter(new FileNameExtensionFilter(
            "圖片檔案 (jpg, jpeg, png, bmp)", "jpg", "jpeg", "png", "bmp"));
        if (fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            loadImage(fc.getSelectedFile().getAbsolutePath());
        }
    }

    private void loadDefault() {
        loadImage(DEFAULT_INPUT);
    }

    private void loadImage(String path) {
        status("載入中...");
        SwingWorker<BufferedImage, Void> worker = new SwingWorker<>() {
            @Override protected BufferedImage doInBackground() throws Exception {
                return loader.load(path);
            }
            @Override protected void done() {
                try {
                    originalImage = get();
                    leftPanel.setImage(originalImage);
                    status("圖片已載入：" + path);
                    applyPipeline();
                } catch (Exception ex) {
                    status("❌ 載入失敗：" + ex.getMessage());
                    JOptionPane.showMessageDialog(CartoonApp.this,
                        "載入失敗：\n" + ex.getMessage(), "錯誤", JOptionPane.ERROR_MESSAGE);
                }
            }
        };
        worker.execute();
    }

    private void applyIfLoaded() {
        if (originalImage != null) applyPipeline();
    }

    private void applyPipeline() {
        pipeline.setEdgeThreshold(sliderEdge.getValue());
        pipeline.setColorLevels(sliderColor.getValue());
        status("處理中...");
        SwingWorker<BufferedImage, Void> worker = new SwingWorker<>() {
            @Override protected BufferedImage doInBackground() {
                return pipeline.process(originalImage);
            }
            @Override protected void done() {
                try {
                    cartoonImage = get();
                    rightPanel.setImage(cartoonImage);
                    status("✅ 卡通化完成！邊緣閾值=" + sliderEdge.getValue()
                           + "  色彩層次=" + sliderColor.getValue());
                } catch (Exception ex) {
                    status("❌ 處理失敗：" + ex.getMessage());
                }
            }
        };
        worker.execute();
    }

    private void saveResult() {
        if (cartoonImage == null) {
            JOptionPane.showMessageDialog(this, "尚未產生卡通圖片！", "提示", JOptionPane.WARNING_MESSAGE);
            return;
        }
        JFileChooser fc = new JFileChooser();
        fc.setSelectedFile(new File("cartoon_output.png"));
        fc.setFileFilter(new FileNameExtensionFilter("PNG 圖片", "png"));
        if (fc.showSaveDialog(this) == JFileChooser.APPROVE_OPTION) {
            String path = fc.getSelectedFile().getAbsolutePath();
            if (!path.toLowerCase().endsWith(".png")) path += ".png";
            try {
                exporter.save(cartoonImage, path);
                status("💾 已儲存：" + path);
            } catch (IOException ex) {
                status("❌ 儲存失敗：" + ex.getMessage());
            }
        }
    }

    private void status(String msg) {
        SwingUtilities.invokeLater(() -> statusLabel.setText(msg));
    }

    // ── 程式入口 ─────────────────────────────────────────────
    public static void main(String[] args) {
        // 套用系統外觀（讓深色背景更自然）
        try { UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName()); }
        catch (Exception ignored) {}

        SwingUtilities.invokeLater(CartoonApp::new);
    }
}
