import time

class DivideAndConquer:
    
    # ==========================================
    # Merge Sort (合併排序)
    # 遞迴關係式: T(n) = 2T(n/2) + n
    # ==========================================
    @staticmethod
    def merge_sort(arr):
        # 基礎條件：陣列長度為 1 或 0 時，已排序完畢
        if len(arr) <= 1:
            return arr

        # Divide (分割): 將陣列從中間切分為兩半
        mid = len(arr) // 2
        
        # Conquer (克服): 遞迴呼叫 merge_sort 處理左右兩半
        # 對應 2T(n/2) 的部分
        left_half = DivideAndConquer.merge_sort(arr[:mid])
        right_half = DivideAndConquer.merge_sort(arr[mid:])

        # Combine (合併): 將排序好的兩半合併
        # 對應 + n 的部分，合併操作需要 O(n) 的時間
        return DivideAndConquer._merge(left_half, right_half)

    @staticmethod
    def _merge(left, right):
        sorted_arr = []
        i = j = 0
        
        # 依序比較左右陣列元素，較小者放入結果陣列
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                sorted_arr.append(left[i])
                i += 1
            else:
                sorted_arr.append(right[j])
                j += 1
                
        # 將剩餘元素加入結果陣列
        sorted_arr.extend(left[i:])
        sorted_arr.extend(right[j:])
        return sorted_arr

    # ==========================================
    # Binary Search (二分搜尋)
    # 遞迴關係式: T(n) = T(n/2) + 1
    # ==========================================
    @staticmethod
    def binary_search(arr, target, low, high):
        # 基礎條件：搜尋區間無效，表示找不到目標
        if low > high:
            return -1

        # Divide (分割): 計算中間索引，時間複雜度 O(1)
        # 對應 + 1 的部分
        mid = (low + high) // 2

        # 檢查中間元素
        if arr[mid] == target:
            return mid
            
        # Conquer (克服): 決定往哪一半繼續搜尋
        # 每次只會選擇其中一半遞迴，對應 T(n/2) 的部分
        elif arr[mid] > target:
            # 目標在左半邊
            return DivideAndConquer.binary_search(arr, target, low, mid - 1)
        else:
            # 目標在右半邊
            return DivideAndConquer.binary_search(arr, target, mid + 1, high)

# 執行範例與驗證
if __name__ == "__main__":
    algo = DivideAndConquer()

    print("=" * 50)
    print(" 演算法展示：Divide and Conquer (分治法)")
    print("=" * 50)

    # 驗證 Merge Sort
    unsorted_data = [38, 27, 43, 3, 9, 82, 10]
    print("\n[1] 合併排序 (Merge Sort)")
    print(f"原始陣列: {unsorted_data}")
    
    start_time_merge = time.perf_counter()
    sorted_data = algo.merge_sort(unsorted_data)
    end_time_merge = time.perf_counter()
    
    print(f"排序結果: {sorted_data}")
    print(f"花費時間: {end_time_merge - start_time_merge:.8f} 秒")

    # 驗證 Binary Search (必須提供已排序陣列)
    target_value = 43
    print(f"\n[2] 二分搜尋 (Binary Search)")
    print(f"在已排序陣列中尋找目標值: {target_value}")
    
    start_time_bs = time.perf_counter()
    result_index = algo.binary_search(sorted_data, target_value, 0, len(sorted_data) - 1)
    end_time_bs = time.perf_counter()
    
    if result_index != -1:
        print(f"搜尋結果: 成功！目標值 {target_value} 位於索引 {result_index}")
    else:
        print(f"搜尋結果: 失敗！找不到目標值 {target_value}")
    print(f"花費時間: {end_time_bs - start_time_bs:.8f} 秒")
    print("\n" + "=" * 50)