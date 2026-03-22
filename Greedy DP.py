import time
import itertools

# -----------------------
# 資料輸入
# -----------------------
weights = [5, 9, 12, 13, 16, 45]  # 範例數字，可自由改
n = len(weights)

# -----------------------
# 貪婪演算法實作 (相鄰合併 - 不使用 Huffman)
# -----------------------
def adjacent_greedy(weights):
    arr = weights[:]
    total_cost = 0

    while len(arr) > 1:
        min_sum = float('inf')
        min_idx = -1
        for i in range(len(arr) - 1):
            if arr[i] + arr[i+1] < min_sum:
                min_sum = arr[i] + arr[i+1]
                min_idx = i
        
        total_cost += min_sum
        arr[min_idx] = min_sum
        del arr[min_idx + 1]

    return total_cost

# -----------------------
# DP 實作 (Optimal Merge Pattern)
# -----------------------
def dp_merge(weights):
    # DP table
    dp = [[0]*n for _ in range(n)]
    # prefix sum for快速計算區間總和
    prefix = [0]*(n+1)
    for i, w in enumerate(weights):
        prefix[i+1] = prefix[i] + w

    # i = start, j = end
    for length in range(2, n+1):  # 子序列長度
        for i in range(n-length+1):
            j = i+length-1
            dp[i][j] = float('inf')
            # k = 分割位置
            for k in range(i, j):
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k+1][j] + prefix[j+1]-prefix[i])
    return dp[0][n-1]

# -----------------------
# 計算時間
# -----------------------
start = time.time()
greedy_cost = adjacent_greedy(weights)
end = time.time()
greedy_time = end - start
print(f"Greedy cost (相鄰合併): {greedy_cost}, time: {greedy_time:.6f}s, complexity: O(n^2)")

start = time.time()
dp_cost = dp_merge(weights)
end = time.time()
dp_time = end - start
print(f"DP cost: {dp_cost}, time: {dp_time:.6f}s, complexity: O(n^3)")

print("-" * 30)
print(f"時間差異 (DP - Greedy): {abs(dp_time - greedy_time):.6f}s")