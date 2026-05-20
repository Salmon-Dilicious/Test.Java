from collections import deque

def display_distance(value):
    return '∞' if value == float('inf') else value

def run_bfs():
    print("=== 1. 廣度優先搜尋 (BFS) ===")
    def bfs_trace(graph, start):
        visited = set([start])
        queue = deque([start])
        traversal_path = []
        
        print(f"【初始狀態】佇列: {list(queue)} | 路徑: {traversal_path}")
        print("-" * 50)
        
        while queue:
            node = queue.popleft()
            traversal_path.append(node)
            print(f"展開節點: [{node}]")
            print(f"  目前路徑更新為: {traversal_path}")
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    print(f"  -> 發現未訪問鄰居: [{neighbor}], 放入佇列: {list(queue)}")
            
            print("-" * 50)
        return traversal_path

    graph = {
        'A': ['B', 'C'],
        'B': ['D', 'E'],
        'C': ['F'],
        'D': [],
        'E': [],
        'F': []
    }
    bfs_trace(graph, 'A')
    print("\n")

def run_dijkstra():
    print("=== 2. Dijkstra 演算法 ===")
    graph = {
        'A': {'B': 1, 'C': 4},
        'B': {'D': 2},
        'C': {'D': 1},
        'D': {}
    }

    distance = {
        'A': float('inf'),
        'B': float('inf'),
        'C': float('inf'),
        'D': float('inf')
    }
    distance['A'] = 0
    visited = []

    while len(visited) < 4:
        min_node = ""
        min_value = float('inf')

        for node in distance:
            if node not in visited and distance[node] < min_value:
                min_value = distance[node]
                min_node = node

        if not min_node:
            break

        print("目前選擇節點：", min_node)
        visited.append(min_node)

        for neighbor in graph.get(min_node, {}):
            old_distance = distance[neighbor]
            new_distance = distance[min_node] + graph[min_node][neighbor]

            print("  檢查", min_node, "->", neighbor)
            print("  原本距離：", display_distance(old_distance))
            print("  新距離：", display_distance(new_distance))

            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                print("  更新成功！")
            else:
                print("  不需要更新")

        print("目前距離表：", {node: display_distance(dist) for node, dist in distance.items()})
        print("-------------------")

    print("最終答案：")
    print(distance)
    print("\n")

def run_bellman_ford():
    print("=== 3. Bellman-Ford 演算法 ===")
    graph = {
        'A': {'B': 1, 'C': 4},
        'B': {'C': -3, 'D': 2},
        'C': {'D': 2},
        'D': {}
    }

    edges = []
    for u in graph:
        for v in graph[u]:
            edges.append((u, v, graph[u][v]))

    distance = {
        'A': float('inf'),
        'B': float('inf'),
        'C': float('inf'),
        'D': float('inf')
    }
    distance['A'] = 0
    V = len(distance)

    print("初始距離表：", {k: display_distance(v) for k, v in distance.items()})
    print("-" * 30)

    for i in range(V - 1):
        print(f"第 {i+1} 輪檢查：")
        updated = False
        
        for u, v, weight in edges:
            old_dist = distance[v]
            new_dist = distance[u] + weight
            
            if distance[u] != float('inf') and new_dist < old_dist:
                print(f"  檢查 {u} -> {v} (權重: {weight:2})：原距離 {display_distance(old_dist):>2}，新距離 {new_dist:2} -> 更新成功！")
                distance[v] = new_dist
                updated = True
            else:
                print(f"  檢查 {u} -> {v} (權重: {weight:2})：不需要更新")
                
        print("  當前距離表：", {k: display_distance(v) for k, v in distance.items()})
        print("-" * 30)
        
        if not updated:
            print("本輪無任何更新，提早結束迴圈。")
            print("-" * 30)
            break

    has_negative_cycle = False
    for u, v, weight in edges:
        if distance[u] != float('inf') and distance[u] + weight < distance[v]:
            has_negative_cycle = True
            break

    print("最終答案：")
    print("最短距離表：", {k: display_distance(v) for k, v in distance.items()})
    print("是否存在負值距離：", any(dist < 0 for dist in distance.values()))
    print("\n")

def run_climbing_stairs():
    print("=== 4. 動態規劃 (爬樓梯) ===")
    n = 5
    dp = [0] * (n + 1)
    
    dp[1] = 1
    dp[2] = 2

    print("第1階有", dp[1], "種方法")
    print("第2階有", dp[2], "種方法")
    print()

    for i in range(3, n + 1):
        print("現在計算第", i, "階")
        print("第", i, "階的方法數 =")
        print("第", i-1, "階的方法數 + 第", i-2, "階的方法數")
        dp[i] = dp[i-1] + dp[i-2]
        print(dp[i-1], "+", dp[i-2], "=", dp[i])
        print()

    print("答案：")
    print("到第", n, "階共有", dp[n], "種方法")
    print("\n")

if __name__ == "__main__":
    run_bfs()
    run_dijkstra()
    run_bellman_ford()
    run_climbing_stairs()