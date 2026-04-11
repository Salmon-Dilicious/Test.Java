from collections import deque

def dfs_iterative(graph, start):
    """
    深度優先搜尋 (使用堆疊)
    為確保與遞迴行為一致（優先訪問左側節點），需將相鄰節點反向推入堆疊。
    """
    visited = set()
    stack = [start]
    result = []

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            stack.extend(reversed(graph[vertex]))
            
    return result

def bfs(graph, start):
    """
    廣度優先搜尋 (使用佇列)
    """
    visited = {start}
    queue = deque([start])
    result = []

    while queue:
        vertex = queue.popleft()
        result.append(vertex)

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
    return result

if __name__ == "__main__":
    print("=" * 60)
    print(" 演算法展示：DFS (深度優先) vs BFS (廣度優先)")
    print("=" * 60)

    user_input = input("\n請輸入多個不重複的節點 (以空白分隔):\n> ").strip()
    if not user_input:
        nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        print("未輸入資料，將使用預設節點: A B C D E F G")
    else:
        nodes = user_input.split()

    # 根據輸入順序建立 Complete Binary Tree (完整二元樹) 的圖結構 (Adjacency List)
    graph = {node: [] for node in nodes}
    for i, node in enumerate(nodes):
        left_index = 2 * i + 1
        right_index = 2 * i + 2
        if left_index < len(nodes):
            graph[node].append(nodes[left_index])
        if right_index < len(nodes):
            graph[node].append(nodes[right_index])

    start_node = nodes[0]

    print("\n[建構完成的圖結構 (Adjacency List)]")
    for node, neighbors in graph.items():
        print(f"節點 {node:2} 往下連接的相鄰節點 -> {neighbors}")

    print("\n" + "-" * 60)
    print(" [1] DFS 深度優先搜尋 (Depth-First Search)")
    print("-" * 60)
    print(f"遍歷順序: {' -> '.join(dfs_iterative(graph, start_node))}")
    print("時間複雜度: O(V + E) - (V為頂點數，E為邊數)")
    print("空間複雜度: O(V)     - (堆疊最大深度)")
    print("特點說明:   優先往深處探索，走到盡頭才回溯 (直向)。")

    print("\n" + "-" * 60)
    print(" [2] BFS 廣度優先搜尋 (Breadth-First Search)")
    print("-" * 60)
    print(f"遍歷順序: {' -> '.join(bfs(graph, start_node))}")
    print("\n" + "=" * 60)