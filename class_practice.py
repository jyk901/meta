"""클래스와 객체 실습 (실행: python3 class_practice.py)

비유: 클래스 = 붕어빵 틀(설계도), 객체 = 틀로 찍어낸 붕어빵
"""

# ── 1단계: 클래스 만들기 ──────────────────────────────
class Dog:                       # 설계도: "강아지는 이름이 있고, 짖을 수 있다"
    def __init__(self, name):    # 객체가 만들어질 때 자동 실행 (초기 설정)
        self.name = name         # self = "나 자신". 이름을 내 것으로 저장

    def bark(self):              # 메서드 = 객체가 할 수 있는 행동
        print(f"{self.name}: 멍멍!")


# ── 2단계: 객체 만들기 (틀로 찍어내기) ────────────────
a = Dog("초코")
b = Dog("두부")
a.bark()   # 초코: 멍멍!
b.bark()   # 두부: 멍멍!   (같은 설계도, 서로 다른 객체)


# ── 3단계: 상태가 변하는 객체 (속성 + 행동) ────────────
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"{self.owner}: {amount}원 입금 → 잔액 {self.balance}원")

    def withdraw(self, amount):
        if amount > self.balance:
            print(f"{self.owner}: 잔액 부족!")
        else:
            self.balance -= amount
            print(f"{self.owner}: {amount}원 출금 → 잔액 {self.balance}원")


kim = Account("김철수", 1000)
lee = Account("이영희")          # 객체마다 잔액이 따로 관리됨
kim.deposit(500)
kim.withdraw(3000)
lee.deposit(200)


# ── 실습 문제 (아래를 직접 채워보세요) ─────────────────
# 문제 1) Cat 클래스를 만들고 meow() 메서드가 "야옹~"을 출력하게 하세요.
# 문제 2) Account에 정보를 출력하는 show() 메서드를 추가해 보세요.
# 문제 3) Student 클래스(name, score 속성, is_pass() 메서드: 60점 이상이면 True)
