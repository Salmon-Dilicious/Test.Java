class User:
    def __init__(self, username, password):
        self.username = username
        self.__password = password

    def check_password(self, input_password):
        return self.__password == input_password


class AuthSystem:
    def __init__(self):
        self.users = []

    def register(self, username, password):
        for user in self.users:
            if user.username == username:
                print("[系統提示] 帳號已被使用，請選擇其他帳號。")
                return

        new_user = User(username, password)
        self.users.append(new_user)
        print(f"[系統提示] 帳號 {username} 註冊成功！")

    def login(self, username, password):
        for user in self.users:
            if user.username == username:
                if user.check_password(password):
                    print(f"[系統提示] 登入成功！歡迎，{username}。")
                else:
                    print("[系統提示] 密碼錯誤，登入失敗。")
                return
        
        print("[系統提示] 找不到此帳號，請先註冊。")


def main():
    system = AuthSystem()

    while True:
        print("\n=== 帳號登入管理系統 ===")
        print("1. 註冊帳號")
        print("2. 登入系統")
        print("3. 離開系統")
        print("========================")
        
        try:
            choice = input("請輸入選項 (1/2/3): ")

            if choice == '1':
                username = input("請輸入新帳號: ")
                password = input("請輸入新密碼: ")
                if not username.strip() or not password.strip():
                    print("[系統提示] 帳號與密碼不能為空白。")
                    continue
                system.register(username, password)

            elif choice == '2':
                username = input("請輸入登入帳號: ")
                password = input("請輸入登入密碼: ")
                system.login(username, password)

            elif choice == '3':
                print("[系統提示] 系統已關閉。")
                break

            else:
                print("[系統提示] 無效的選項，請輸入 1、2 或 3。")
                
        except KeyboardInterrupt:
            print("\n[系統提示] 偵測到強制中斷，系統安全關閉。")
            break
        except Exception as e:
            print(f"[系統錯誤] 發生未預期的錯誤: {e}")

if __name__ == "__main__":