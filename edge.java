import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

public class edge {
    public static void main(String[] args) {
        String inputDir = "C:\\Users\\User\\Pictures\\123465";
        String outputDir = "C:\\Users\\User\\Pictures\\outpit";

        File inDir = new File(inputDir);
        if (!inDir.exists() || !inDir.isDirectory()) {
            System.out.println("輸入資料夾不存在: " + inputDir);
            return;
        }

        File[] imageFiles = inDir.listFiles((dir, name) -> {
            String lower = name.toLowerCase();
            return lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".png") || lower.endsWith(".bmp");
        });

        if (imageFiles == null || imageFiles.length == 0) {
            System.out.println("資料夾中找不到支援的影像檔案: " + inputDir);
            return;
        }

        // 建立輸出資料夾
        File outDirFile = new File(outputDir);
        if (!outDirFile.exists()) {
            outDirFile.mkdirs();
        }

        for (File imageFile : imageFiles) {
            processImage(imageFile, outDirFile);
        }
    }

    private static void processImage(File inputFile, File outputDir) {
        try {
            BufferedImage img = ImageIO.read(inputFile);
            if (img == null) {
                System.out.println("無法讀取影像: " + inputFile.getName());
                return;
            }

            int width = img.getWidth();
            int height = img.getHeight();

            BufferedImage outImgX = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
            BufferedImage outImgY = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);

            // 擷取影像並轉換為灰階陣列
            int[][] gray = new int[width][height];
            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                    int p = img.getRGB(x, y);
                    int r = (p >> 16) & 0xff;
                    int g = (p >> 8) & 0xff;
                    int b = p & 0xff;
                    // 使用 NTSC 轉換公式
                    gray[x][y] = (int)(0.299 * r + 0.587 * g + 0.114 * b);
                }
            }

            // 執行有限差分 (Finite Differences) 運算
            for (int y = 1; y < height - 1; y++) {
                for (int x = 1; x < width - 1; x++) {
                    // X方向偏導數: [f(x+1, y) - f(x-1, y)] / 2
                    int dx = (gray[x + 1][y] - gray[x - 1][y]) / 2;
                    // Y方向偏導數: [f(x, y+1) - f(x, y-1)] / 2
                    int dy = (gray[x][y + 1] - gray[x][y - 1]) / 2;

                    // 梯度值域包含負數，平移 128 產生投影片中灰階背景的浮雕視覺效果
                    int pixelX = Math.min(Math.max(dx + 128, 0), 255);
                    int pixelY = Math.min(Math.max(dy + 128, 0), 255);

                    // 寫入對應的 RGB 通道
                    outImgX.setRGB(x, y, (pixelX << 16) | (pixelX << 8) | pixelX);
                    outImgY.setRGB(x, y, (pixelY << 16) | (pixelY << 8) | pixelY);
                }
            }

            // 取得輸入檔案名稱（不含副檔名）
            String baseName = inputFile.getName();
            int dotIndex = baseName.lastIndexOf('.');
            if (dotIndex > 0) {
                baseName = baseName.substring(0, dotIndex);
            }

            // 輸出 X 軸與 Y 軸的偏導數影像
            ImageIO.write(outImgX, "jpg", new File(outputDir, baseName + "_dx.jpg"));
            ImageIO.write(outImgY, "jpg", new File(outputDir, baseName + "_dy.jpg"));
            System.out.println("完成: " + inputFile.getName() + " -> " + baseName + "_dx.jpg, " + baseName + "_dy.jpg");

        } catch (Exception e) {
            System.out.println("處理檔案失敗: " + inputFile.getName());
            e.printStackTrace();
        }
    }
}
