import heapq
import time

# 建立 Huffman 樹的節點
class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # 比較節點大小（給 heapq 用）
    def __lt__(self, other):
        return self.freq < other.freq

# 建立 Huffman 樹
def build_huffman_tree(frequencies):
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)  # O(n)
    
    while len(heap) > 1:  # 迴圈 n-1 次
        left = heapq.heappop(heap)  # O(log n)
        right = heapq.heappop(heap) # O(log n)
        merged = Node(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)  # O(log n)
    
    return heap[0]  # 根節點

# 生成 Huffman 編碼表
def generate_codes(node, prefix="", code_table={}):
    if node is None:
        return
    if node.char is not None:  # 葉節點
        code_table[node.char] = prefix
    generate_codes(node.left, prefix + "0", code_table)
    generate_codes(node.right, prefix + "1", code_table)
    return code_table

# 範例字串
text = "this is an example for huffman encoding"
frequencies = {}
for char in text:
    frequencies[char] = frequencies.get(char, 0) + 1

# 計時
start_time = time.time()
root = build_huffman_tree(frequencies)
codes = generate_codes(root)
end_time = time.time()

# 顯示 Huffman 編碼
print("Character codes (依出現頻率排序，展示次數與編碼長度的反比關係):")
print(f"{'字元':<5} | {'出現次數':<8} | {'編碼長度 (大小)':<14} | {'Huffman 編碼'}")
print("-" * 55)
# 將字元依出現頻率排序 (由小到大)
for char, freq in sorted(frequencies.items(), key=lambda item: item[1]):
    print(f"'{char}'   | {freq:<12} | {len(codes[char]):<18} | {codes[char]}")

print("\nOriginal text length (bits):", len(text)*8)
encoded_text = "".join(codes[char] for char in text)
print("Encoded text length (bits):", len(encoded_text))
print("Time elapsed:", end_time - start_time, "seconds")

# 顯示 Big O 時間複雜度
print("\n=== Big O 時間複雜度 (Time Complexity) ===")
print("1. 計算字元頻率: O(L), L 為字串總長度")
print("2. 建立 Huffman 樹 (Priority Queue): O(n log n), n 為不重複字元的數量")
print("--> 總時間複雜度: O(n log n)")