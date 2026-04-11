class TreeNode:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if self.root is None:
            self.root = TreeNode(key)
        else:
            self._insert(self.root, key)

    def _insert(self, node, key):
        if key < node.val:
            if node.left is None:
                node.left = TreeNode(key)
            else:
                self._insert(node.left, key)
        elif key >= node.val:
            if node.right is None:
                node.right = TreeNode(key)
            else:
                self._insert(node.right, key)

    def display(self, node, level=0, prefix="Root: "):
        if node is not None:
            self.display(node.left, level + 1, "L--- ")
            print(" " * (level * 4) + prefix + str(node.val))
            self.display(node.right, level + 1, "R--- ")

if __name__ == "__main__":
    bst = BinarySearchTree()
    while True:
        try:
            user_input = input("輸入整數以新增節點 (輸入 q 結束): ")
            if user_input.strip().lower() == 'q':
                break
            num = int(user_input)
            bst.insert(num)
            print("\n當前二元搜尋樹結構:")
            bst.display(bst.root)
            print("-" * 40)
        except ValueError:
            print("無效輸入，請輸入整數。")