import sys

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    elif val > root.val:
        root.right = insert(root.right, val)
    return root

def preorder_traversal(root):
    result = []
    def traverse(node):
        if node:
            result.append(str(node.val))
            traverse(node.left)
            traverse(node.right)
    traverse(root)
    return " -> ".join(result)

def inorder_traversal(root):
    result = []
    def traverse(node):
        if node:
            traverse(node.left)
            result.append(str(node.val))
            traverse(node.right)
    traverse(root)
    return " -> ".join(result)

def postorder_traversal(root):
    result = []
    def traverse(node):
        if node:
            traverse(node.left)
            traverse(node.right)
            result.append(str(node.val))
    traverse(root)
    return " -> ".join(result)

def main():
    root = None
    print("【 Tree Traversal 終端機實作 】")
    print("指令說明：")
    print("1. 輸入 [整數] 建立並插入節點")
    print("2. 輸入 [show] 輸出當前 Preorder, Inorder, Postorder 走訪結果")
    print("3. 輸入 [exit] 結束程式\n")
    
    while True:
        try:
            user_input = input("請輸入數值或指令: ").strip()
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'show':
                if not root:
                    print("目前為空樹。")
                    continue
                print(f"Preorder  (前序): {preorder_traversal(root)}")
                print(f"Inorder   (中序): {inorder_traversal(root)}")
                print(f"Postorder (後序): {postorder_traversal(root)}\n")
            else:
                val = int(user_input)
                root = insert(root, val)
                print(f"已插入數值: {val}")
        except ValueError:
            print("錯誤：僅接受整數數值或 show/exit 指令。")

if __name__ == "__main__":
    main()