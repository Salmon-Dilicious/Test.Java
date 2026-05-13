import argparse
import cv2
import numpy as np
import time
import os
import glob
from collections import deque


def compute_prefix_sums(hist):
    """建立 cumulative sum 以達 O(1) 區間統計量計算"""
    hist_sum = hist.sum()
    if hist_sum <= 0:
        return np.zeros(len(hist) + 1), np.zeros(len(hist) + 1), np.zeros(len(hist) + 1)

    P = hist / hist_sum
    L = len(P)

    S0 = np.zeros(L + 1)
    S1 = np.zeros(L + 1)
    S2 = np.zeros(L + 1)

    for i in range(L):
        S0[i + 1] = S0[i] + P[i]
        S1[i + 1] = S1[i] + i * P[i]
        S2[i + 1] = S2[i] + (i**2) * P[i]

    return S0, S1, S2


def get_region_variance(S0, S1, S2, left, right):
    """根據 cumulative sum 計算區間 [left, right] 的組內變異數"""
    if left > right:
        return 0.0

    q = S0[right + 1] - S0[left]
    if q <= 0:
        return 0.0

    sum1 = S1[right + 1] - S1[left]
    sum2 = S2[right + 1] - S2[left]

    mean = sum1 / q
    variance = sum2 - 2 * mean * sum1 + (mean**2) * q
    return variance


def bfs_multi_threshold(S0, S1, S2, num_thresholds=2):
    """BFS 廣度優先搜尋最佳 threshold 組合"""
    L = len(S0) - 1
    best_var = float('inf')
    best_thresholds = None

    start_state = tuple(range(1, num_thresholds + 1))
    queue = deque([start_state])
    visited = {start_state}

    while queue:
        current_t = queue.popleft()

        boundaries = [0] + list(current_t) + [L - 1]
        total_var = 0.0
        for i in range(len(boundaries) - 1):
            left = boundaries[i] if i == 0 else boundaries[i] + 1
            right = boundaries[i + 1]
            total_var += get_region_variance(S0, S1, S2, left, right)

        if total_var < best_var:
            best_var = total_var
            best_thresholds = current_t

        for i in range(num_thresholds):
            new_t = list(current_t)
            new_t[i] += 1

            is_valid = True
            if new_t[i] >= L - 1:
                is_valid = False
            if i < num_thresholds - 1 and new_t[i] >= new_t[i + 1]:
                is_valid = False

            if is_valid:
                new_state = tuple(new_t)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append(new_state)

    return best_thresholds


def get_image_paths(in_dir):
    patterns = [
        "*.png", "*.jpg", "*.jpeg", "*.bmp",
        "*.tiff", "*.tif", "*.gif"
    ]
    image_paths = []
    for pattern in patterns:
        image_paths.extend(glob.glob(os.path.join(in_dir, pattern)))
    return sorted(image_paths)


def process_images(in_dir, out_dir, k_thresholds=2):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    image_paths = get_image_paths(in_dir)
    if not image_paths:
        print(f"找不到圖片：{in_dir}")
        return

    print(f"找到 {len(image_paths)} 張圖片，輸出至 {out_dir}")

    for img_path in image_paths:
        filename = os.path.basename(img_path)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            print(f"無法讀取檔案：{filename}")
            continue

        start_time = time.perf_counter()

        hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_sum = hist.sum()
        if hist_sum <= 0:
            print(f"警告：圖片 {filename} 的 histogram 為空，跳過")
            continue

        S0, S1, S2 = compute_prefix_sums(hist)

        best_t = bfs_multi_threshold(S0, S1, S2, num_thresholds=k_thresholds)
        if best_t is None:
            print(f"警告：未找到最佳 threshold，使用預設值")
            best_t = tuple(range(1, k_thresholds + 1))

        segmented_img = np.zeros_like(img)
        boundaries = [0] + list(best_t) + [255]
        colors = np.linspace(0, 255, len(boundaries) - 1).astype(np.uint8)
        for i in range(len(boundaries) - 1):
            left = boundaries[i] if i == 0 else boundaries[i] + 1
            right = boundaries[i + 1]
            condition = (img >= left) & (img <= right)
            segmented_img[condition] = colors[i]

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        print(f"File: {filename}")
        print(f"最佳 Threshold 組合: {best_t}")
        print(f"執行時間: {execution_time:.4f} 秒")
        print(f"時間複雜度: O(L^k) = O(256^{k_thresholds})，空間複雜度: O(L^k)")
        print("-" * 30)

        out_path = os.path.join(out_dir, filename)
        cv2.imwrite(out_path, segmented_img)


def main():
    parser = argparse.ArgumentParser(description="多閾值影像分割")
    parser.add_argument("--in_dir", default=r"C:\Users\user\Pictures\inpicture", help="輸入資料夾路徑")
    parser.add_argument("--out_dir", default=r"C:\Users\user\Pictures\outpicture", help="輸出資料夾路徑")
    parser.add_argument("--k", type=int, default=2, help="閾值數量 (預設 2)")
    args = parser.parse_args()

    process_images(args.in_dir, args.out_dir, k_thresholds=args.k)


if __name__ == "__main__":
    main()
