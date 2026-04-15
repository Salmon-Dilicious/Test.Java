import math
from collections import deque

# ==========================================
# Question 1: Sorting (Bubble Sort)
# ==========================================
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

print("--- Question 1 ---")
print(bubble_sort([5, 1, 4, 2, 8]))


# ==========================================
# Question 2: Recurrence / Recursive Thinking
# ==========================================
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print("\n--- Question 2 ---")
print(factorial(5))


# ==========================================
# Question 3: Greedy and Dynamic Programming
# ==========================================
def min_coins(amount):
    coins = [25, 10, 5, 1]
    result = []
    for coin in coins:
        while amount >= coin:
            amount -= coin
            result.append(coin)
    return len(result), result

print("\n--- Question 3 ---")
count, selected = min_coins(63)
print(f"{count} coins; {selected}")


# ==========================================
# Question 4: Tree Construction and Search
# ==========================================
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def dfs_search(root, target):
    if not root:
        return False
    if root.val == target:
        return True
    return dfs_search(root.left, target) or dfs_search(root.right, target)

print("\n--- Question 4 ---")
root = TreeNode(5)
root.left = TreeNode(3, TreeNode(2), TreeNode(4))
root.right = TreeNode(8, None, TreeNode(7))

if dfs_search(root, 7):
    print("Found")
else:
    print("Not Found")


# ==========================================
# Question 5: Stack and Queue
# ==========================================
print("\n--- Question 5 ---")
stack = []
stack.append(10)
stack.append(20)
stack.pop()
stack.append(30)

queue = deque()
queue.append(10)
queue.append(20)
queue.popleft()
queue.append(30)

print(f"Stack: {stack}; Queue: {list(queue)}")


# ==========================================
# Question 6: Linked List
# ==========================================
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

print("\n--- Question 6 ---")
head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
curr = head
res = []
while curr:
    res.append(str(curr.val))
    curr = curr.next

print(" ".join(res))


# ==========================================
# Question 7: Nearest Neighbor Classifier
# ==========================================
def l1_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def l2_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

print("\n--- Question 7 ---")
points = {'A': (1, 1), 'B': (4, 4), 'C': (6, 1)}
p = (3, 2)

nearest_l1 = min(points, key=lambda k: l1_distance(p, points[k]))
nearest_l2 = min(points, key=lambda k: l2_distance(p, points[k]))

if nearest_l1 == nearest_l2:
    print(f"Nearest under both L1 and L2: {nearest_l1}")