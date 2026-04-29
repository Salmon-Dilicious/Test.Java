import cv2
import os
import numpy as np

def detect_and_draw_objects(image_path, output_path):
    if not os.path.exists(image_path):
        print(f"找不到圖片：{image_path}")
        return

    print(f"正在分析圖片：{image_path}")
    # 讀取圖片
    img = cv2.imread(image_path)
    if img is None:
        print("圖片讀取失敗。")
        return

    # 1. 轉換為灰階
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1.5 增加對比度 (CLAHE) - 讓圖片邊緣與細節更明顯
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 2. 雙邊濾波去噪 (取代高斯模糊) - 能保留邊緣的同時去除雜訊，讓輪廓更清晰
    # 針對細節，縮小濾波範圍 d=5，避免過度模糊
    blurred = cv2.bilateralFilter(enhanced, 5, 75, 75)
    
    # 3. 邊緣偵測 (Canny 演算法)
    # 自動計算 Canny 的上下限閾值，適應不同明暗度的圖片
    median_val = np.median(blurred)
    lower_thresh = int(max(0, (1.0 - 0.33) * median_val))
    upper_thresh = int(min(255, (1.0 + 0.33) * median_val))
    edges = cv2.Canny(blurred, lower_thresh, upper_thresh)

    # 3.5 形態學「閉運算」 (Morphological Closing)
    # 為了保留文具等小物體的細節，大幅減弱閉運算強度，避免物體被黏合成一團
    kernel = np.ones((7, 7), np.uint8)
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 4. 尋找圖片中的封閉輪廓 (改用 closed_edges)
    contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 建立一張與原圖大小相同，且全黑的背景
    result_img = np.zeros_like(gray)

    count = 0
    # 5. 將找到的目標物畫在黑底上
    for contour in contours:
        # 稍微降低面積門檻，確保能抓到 H
        if cv2.contourArea(contour) > 100:
            # 將目標物輪廓內部填滿為純白 (厚度參數設為 -1 代表填滿)
            cv2.drawContours(result_img, [contour], -1, 255, -1)
            count += 1
            
    print(f"掃描完成！共標記了 {count} 個主要區塊。")
    cv2.imwrite(output_path, result_img)
    print(f"結果已儲存為新圖片：{output_path}")

if __name__ == "__main__":
    input_img = r'C:\Users\user\Pictures\Saved Pictures\getImage.jpg'
    output_img = r'C:\Users\user\Pictures\Saved Pictures\detected_getImage.jpg'
    detect_and_draw_objects(input_img, output_img)