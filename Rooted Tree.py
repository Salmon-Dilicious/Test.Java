class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class Tree:
    """封裝樹狀結構的資料與操作，提高未來擴充性"""
    def __init__(self, root_value):
        self.root = TreeNode(root_value)
        self.nodes = {root_value: self.root}

    def add_node(self, parent_value, child_value):
        """新增節點並處理防呆機制"""
        if parent_value not in self.nodes:
            return False, f"父節點 '{parent_value}' 不存在。"
        if child_value in self.nodes:
            return False, f"節點 '{child_value}' 已存在，避免名稱重複造成覆蓋。"
        
        new_node = TreeNode(child_value)
        self.nodes[parent_value].add_child(new_node)
        self.nodes[child_value] = new_node
        return True, "新增成功。"

    def print_tree(self, node=None, level=0):
        """使用遞迴與縮進在終端機顯示樹狀結構"""
        if node is None:
            node = self.root
            
        indent = "    " * level
        connector = "|-- " if level > 0 else ""
        print(f"{indent}{connector}{node.value}")
        for child in node.children:
            self.print_tree(child, level + 1)

def build_custom_tree():
    """
    互動式建立樹狀結構
    """
    print("--- Rooted Tree 建立程式 ---")
    root_val = input("請輸入根節點 (Root) 的值: ")
    tree = Tree(root_val)

    while True:
        print("\n" + "="*30)
        print("目前樹狀結構:")
        tree.print_tree()
        
        print("\n[功能選單]")
        print("1: 新增節點")
        print("2: 結束並顯示結果")
        # TODO: 未來可在此擴充其他指令 (如：3: 刪除節點, 4: 搜尋節點, 5: 匯出成 JSON)
        
        cmd = input("\n輸入指令: ")
        
        if cmd == '1':
            parent_val = input("輸入父節點的值: ")
            child_val = input("輸入新節點的值: ")
            success, msg = tree.add_node(parent_val, child_val)
            if not success:
                print(f"錯誤：{msg}")
        elif cmd == '2':
            break
        else:
            print("無效指令，請重新輸入。")

    print("\n" + "="*30)
    print("最終樹狀結構結果:")
    tree.print_tree()

if __name__ == "__main__":
    build_custom_tree()