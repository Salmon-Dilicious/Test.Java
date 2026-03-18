class Queue:
    def __init__(self):
        self.items = []

    # 加入（後面）
    def enqueue(self, value):
        self.items.append(value)
        print(f"放入: {value}")

    # 取出（前面）
    def dequeue(self):
        if not self.items:
            print("Queue 是空的！")
        else:
            print(f"取出: {self.items.pop(0)}")

    # 查看最前面
    def peek(self):
        if not self.items:
            print("Queue 是空的！")
        else:
            print(f"最前面 (front): {self.items[0]}")

    # 顯示（清楚標示 front / rear）
    def show(self):
        if not self.items:
            print("Queue 是空的！")
            return
        
        print("\n目前 Queue（前 → 後）:")
        print("Front → ", end="")
        for item in self.items:
            print(item, end=" ")
        print("← Rear")


q = Queue()

while True:
    print("\n請選擇操作：")
    print("1: 放入數字 (enqueue)")
    print("2: 取出數字 (dequeue)")
    print("3: 查看最前面 (front)")
    print("4: 顯示 Queue")
    print("5: 離開")

    choice = input("輸入選項: ")

    if choice == "1":
        num = input("請輸入數字: ")
        
        # 防呆：只能輸入整數
        if num.lstrip("-").isdigit():
            q.enqueue(int(num))
        else:
            print("❌ 請輸入「整數」！")

    elif choice == "2":
        q.dequeue()

    elif choice == "3":
        q.peek()

    elif choice == "4":
        q.show()

    elif choice == "5":
        print("程式結束")
        break

    else:
        print("請輸入正確選項！")