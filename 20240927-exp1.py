import math
import calendar
import random


def question1():
    print("Input (x1, y1) and (x2, y2) to calculate the distance.")
    x1 = float(input("x1:"))
    x2 = float(input("x2:"))
    y1 = float(input("y1:"))
    y2 = float(input("y2:"))
    print(f"Distance is {math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))}")


def question2():
    year = int(input("Input a year to print the calendar: "))
    month = int(input(f"Input the month of {year}: "))
    print(calendar.month(year, month))


def question3():
    y = int(input("Input a year to judge whether the year is leap year or not: "))
    print(f"{y} is {'' if (y%4==0 and y%100!=0) or y%400==0 else 'not '}leap year.")


def question4():
    print("Input three numbers and then will sort them.")
    l = [
        eval(input("Input number1: ")),
        eval(input("Input number2: ")),
        eval(input("Input number3: ")),
    ]
    l.sort()
    print(f"The numbers after sorted: [{', '.join(str(n) for n in l)}]")


def question5():
    result = []
    for j in range(100, 999):
        if math.pow(j // 100, 3) + math.pow(j // 10 % 10, 3) + math.pow(j % 10, 3) == j:
            result.append(j)
    print(f"There are numbers of Narcissus: [{', '.join(str(n) for n in result)}]")


def question6():
    guess = -1
    answer = random.randint(0, 10)
    while guess != answer:
        guess = int(input("Guess the random number: "))
        if guess > answer:
            print("Bigger! Try again.")
        elif guess < answer:
            print("Lesser! Try again.")
    print("Bingo!")


def question7():
    point = 0
    for k in range(5):
        a = random.randint(0, 100)
        b = random.randint(0, 100)
        c = int(input(f"{a}+{b}="))
        if c == a + b:
            point += 1
            print("回答正确，加一分")
        else:
            print("回答错误，不加分")
    print(f"您的总分为: {point}")
    if point >= 4:
        print("恭喜您，闯关成功！")
    else:
        print("很遗憾，闯关失败！")


question7()
