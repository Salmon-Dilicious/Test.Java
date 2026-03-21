class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.pass_count = 0

class BookSearchTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.pass_count += 1
        node.is_end_of_word = True

    def search_and_predict(self, prefix: str):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return [], None
            node = node.children[char]

        matched_books = []
        self._dfs(node, prefix, matched_books)

        predicted_char = None
        if node.children:
            predicted_char = max(node.children.items(), key=lambda item: item[1].pass_count)[0]

        return matched_books, predicted_char

    def _dfs(self, node, current_path, result):
        if node.is_end_of_word:
            result.append(current_path)
        for char, child_node in node.children.items():
            self._dfs(child_node, current_path + char, result)

books = [
    "apple", "application", "apply", "banana", "book",
    "cat", "computer", "computation", "data", "database",
    "algorithm", "artificial intelligence", "biology", "chemistry",
    "design patterns", "deep learning", "economics", "engineering",
    "finance", "fundamentals of physics", "geometry", "history",
    "information retrieval", "java programming", "javascript basics",
    "machine learning", "mathematics", "network security", "operating systems",
    "python programming", "quantum mechanics", "software engineering"
]

trie = BookSearchTrie()
for book in books:
    trie.insert(book)

print("=== 歡迎使用書籍搜尋預測系統 ===")
print("您可以逐字輸入來觀察預測結果，輸入 'exit' 離開系統。\n")

current_prefix = ""
while True:
    if current_prefix:
        user_input = input(f"目前輸入為 '{current_prefix}'，請接續輸入下一個字母 (輸入 'clear' 重新查詢，'exit' 離開): ").lower()
    else:
        user_input = input("請輸入想查詢的書名第一個英文字 (輸入 'exit' 離開): ").lower()

    if user_input == 'exit':
        break
    elif user_input == 'clear':
        current_prefix = ""
        print("-" * 30)
        continue

    current_prefix += user_input
    matched_books, next_char = trie.search_and_predict(current_prefix)

    print(f"\n以 '{current_prefix}' 開頭的符合書名:")
    if not matched_books:
        print("  (找不到相關書籍)")
    else:
        for i, book in enumerate(matched_books, 1):
            print(f"  {i}. {book}")

    if next_char:
        print(f"\n最可能的下一個字母預測: {next_char}")
    else:
        print("\n沒有可預測的下一個字母")
    print("-" * 30 + "\n")