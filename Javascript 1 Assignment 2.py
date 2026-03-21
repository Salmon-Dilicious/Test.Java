import random
import sys

# 確保 Python 在 Telnet 上輸出中文不亂碼
sys.stdout.reconfigure(encoding='utf-8')

# 定義 Learner 類別
class Learner:
    def __init__(self, memory_capacity):
        self.memory = []
        self.memory_capacity = memory_capacity
        self.current_choice = None

    # 選擇行動
    def choose(self):
        if self.memory:
            self.current_choice = max(set(self.memory), key=self.memory.count)
        else:
            self.current_choice = random.randint(1, 5)
        return self.current_choice

    # 學習結果
    def learn(self, outcome):
        self.memory.append(outcome)
        if len(self.memory) > self.memory_capacity:
            self.memory.pop(0)

# 模擬環境
def simulate(learner, total_steps=20, change_at=10):
    best_choice = 1
    adapt_time = None
    old_best = best_choice
    gratitude_count = 0
    stubborn_count = 0

    for t in range(total_steps):
        choice = learner.choose()

        # 環境改變
        if t >= change_at:
            best_choice = 3

        # 計算感恩/固執
        if choice == old_best:
            if t >= change_at:
                stubborn_count += 1
            else:
                gratitude_count += 1

        # 記錄適應新環境的時間
        if t >= change_at and adapt_time is None and choice == best_choice:
            adapt_time = t - change_at + 1

        learner.learn(best_choice)

    gratitude_score = gratitude_count / change_at
    stubborn_score = stubborn_count / (total_steps - change_at)
    return adapt_time, gratitude_score, stubborn_score

memory_list = [1, 3, 10]

for mem in memory_list:
    learner = Learner(memory_capacity=mem)
    adapt_time, gratitude_score, stubborn_score = simulate(learner)
    
    print(f"==============================")
    print(f"記憶容量: {mem}")
    print(f"環境改變後適應時間: {adapt_time}")
    print(f"Gratitude score: {gratitude_score:.2f}")
    print(f"Stubborn score: {stubborn_score:.2f}")