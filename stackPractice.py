class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)
        print(f"放入: {value}")

    def pop(self):
        if not self.items:
            print("Stack 是空的！")
        else:
            print(f"取出: {self.items.pop()}")

    def peek(self):
        if not self.items:
            print("Stack 是空的！")
        else:
            print(f"最上面 (top): {self.items[-1]}")

    def show(self):
        if not self.items:
            print("Stack 是空的！")
            return
        
        print("\n目前 Stack（上 → 下）:")
        print("------")
        # 反過來印，讓上面在上面
        for item in reversed(self.items):
            print(f"| {item} |")
        print("------")

s = Stack()

while True:
    print("\n請選擇操作：")
    print("1: 放入數字 (push)")
    print("2: 取出數字 (pop)")
    print("3: 查看最上面 (top)")
    print("4: 顯示 Stack")
    print("5: 離開")

    choice = input("輸入選項: ")

    if choice == "1":
        num = input("請輸入數字: ")
        
        #  防呆：只能輸入數字
        if num.lstrip("-").isdigit():
            s.push(int(num))
        else:
            print("❌ 請輸入「整數」！")

    elif choice == "2":
        s.pop()

    elif choice == "3":
        s.peek()

    elif choice == "4":
        s.show()

    elif choice == "5":
        print("程式結束")
        break

    else:
        print("請輸入正確選項！")