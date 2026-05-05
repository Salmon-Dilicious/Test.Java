import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

public class ImageSegmentation {

    public static void main(String[] args) {
        // 設定輸入與輸出檔案路徑
        String inputPath = "C:\\Users\\User\\Pictures\\ImageGet\\123.jpg";
        String outputPath = "C:\\Users\\User\\Pictures\\ImageGet\\output.png";

        try {
            File inputFile = new File(inputPath);
            if (!inputFile.exists()) {
                System.out.println("找不到輸入影像：" + inputPath);
                return;
            }
            BufferedImage image = ImageIO.read(inputFile);

            int width = image.getWidth();
            int height = image.getHeight();
            int totalPixels = width * height;

            // 1. 轉換灰階並建立直方圖 (Histogram)
            int[] histogram = new int[256];
            int[][] grayPixels = new int[width][height];

            for (int x = 0; x < width; x++) {
                for (int y = 0; y < height; y++) {
                    int rgb = image.getRGB(x, y);
                    int r = (rgb >> 16) & 0xFF;
                    int g = (rgb >> 8) & 0xFF;
                    int b = rgb & 0xFF;
                    
                    // 使用亮度公式轉換灰階
                    int gray = (int) (0.299 * r + 0.587 * g + 0.114 * b);
                    grayPixels[x][y] = gray;
                    histogram[gray]++;
                }
            }

            // 2. 計算最佳門檻值 (T_opt) - 尋找最大類間變異數 (等同於最小群內變異數)
            float sum = 0;
            for (int i = 0; i < 256; i++) {
                sum += i * histogram[i];
            }

            float sumB = 0;
            int wB = 0;
            int wF = 0;
            float varMax = 0;
            int threshold = 0;

            for (int i = 0; i < 256; i++) {
                wB += histogram[i];
                if (wB == 0) continue;
                
                wF = totalPixels - wB;
                if (wF == 0) break;

                sumB += (float) (i * histogram[i]);
                
                float mB = sumB / wB;
                float mF = (sum - sumB) / wF;

                // 類間變異數公式
                float varBetween = (float) wB * (float) wF * (mB - mF) * (mB - mF);

                if (varBetween > varMax) {
                    varMax = varBetween;
                    threshold = i;
                }
            }

            System.out.println("計算得出之最佳門檻值 (T_opt): " + threshold);

            // 3. 根據 T_opt 進行影像分割 (Segmentation)
            BufferedImage outputImage = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_BINARY);
            for (int x = 0; x < width; x++) {
                for (int y = 0; y < height; y++) {
                    if (grayPixels[x][y] >= threshold) {
                        outputImage.setRGB(x, y, 0xFFFFFFFF); // 前景設為白色
                    } else {
                        outputImage.setRGB(x, y, 0xFF000000); // 背景設為黑色
                    }
                }
            }

            // 儲存分割後的影像
            ImageIO.write(outputImage, "png", new File(outputPath));
            System.out.println("影像分割完成，已輸出至: " + outputPath);

        } catch (IOException e) {
            System.err.println("影像處理發生錯誤: " + e.getMessage());
        }
    }
}