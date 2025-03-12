"""
Author: aquamarine5 && aquamarine5_@outlook.com
Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
"""


def question1():
    print(
        f"三个数中最大的数字为 {max(int(input(f'请输入第{iter}个数：')) for iter in ['一', '二', '三'])}"
    )


def question2():
    char = input("请输入一个字符：")
    print(
        f"输出的字符为：{char.lower() if char.isupper() else (char.upper() if char.islower() else char)}"
    )


def question3():
    ans = 1
    for i in range(2, (num := int(input("请输入一个小于10的整数："))) + 1):
        ans *= i
    print(f"1到{num}的乘积为：{ans}")


def question4():
    while (volume := (l := 1) ** 3) <= 100:
        print(f"棱长为{l}的立方体的体积为：{volume}")
        l += 1


def question5():
    while (value := int(input("请输入一个数字："))) != 0:
        c = 0
        clist = []
        for i in range(1, (value // 2) + 1):
            if value % i == 0:
                c += i
                clist.append(str(i))
        print(
            f"{'+'.join(clist)}{'=' if c == value else ('<' if c < value else '>')}{value}"
        )
        print(
            f"{c}是{'完全数' if c == value else ('不足数' if c < value else '丰沛数')}"
        )
    print("程序结束！")


def question6():
    def factorial(x: int) -> int:
        r = 1
        for i in range(2, x + 1):
            r *= i
        return r

    ans = 0
    for i in range(1, 10, 2):
        ans += factorial(i)
    print(f"The result is {ans}")


def question7():
    def isprime(x: int) -> bool:
        for i in range(2, (x // 2) + 1):
            if x % i == 0:
                return False
        return True

    primeCount = 1
    for i in range(100, 301):
        if isprime(i):
            print(i, end=" ")
            primeCount += 1
        if primeCount >= 8:
            print("\n")
            primeCount = 1


def question8():
    def removeEx(l: list[str], v: str) -> list[str]:
        (r := l.copy()).remove(v)
        return r

    numlist = ["1", "2", "3", "4"]
    numcount = 0
    for firstnum in numlist:
        for secondnum in removeEx(numlist, firstnum):
            for thirdnum in removeEx(removeEx(numlist, firstnum), secondnum):
                numcount += 1
                print(firstnum + secondnum + thirdnum, end=" ")
                if numcount % 8 == 0:
                    print("\n")
    print(f"There are {numcount} non repeating numbers that meet the requirements.")


def question9():
    print("Da Yan Sequence:")
    for i in range(1, 21):
        if i % 2 == 0:
            print(f"{(i ** 2) // 2:03d}", end=" ")
        else:
            print(f"{(i ** 2 - 1) // 2:03d}", end=" ")
        if i % 5 == 0:
            print("\n")


def question10():
    buf = 0
    bbuf = 1
    print("00001", end=" ")
    for i in range(2, 25):
        tmp = bbuf
        bbuf += buf
        buf = tmp
        print(f"{bbuf:05d}", end=" ")
        if i % 6 == 0:
            print("\n")


def question11():
    rosenums = []
    for i in range(1000, 9999):
        if (
            (i // 1000) ** 4
            + (i // 100 % 10) ** 4
            + (i // 10 % 10) ** 4
            + (i % 10) ** 4
        ) == i:
            rosenums.append(str(i))
    print(f"The four leaf rose numbers: {' '.join(rosenums)}")


def question12():
    isomorphicnums = []
    isomorphicnums.co
    for i in range(1, 101):
        if str(i**2).endswith(str(i)):
            isomorphicnums.append(str(i))
    print(f"Isomorphic numbers: {' '.join(isomorphicnums)}")


def question13():
    import math

    criterianums = []
    for i in range(1, 5001):
        if math.sqrt(i + 100) % 1 == 0 and math.sqrt(i + 268) % 1 == 0:
            criterianums.append(str(i))
    print(f"Integers that meets this condition: {' '.join(criterianums)}")


def question14():
    ia = int(input("请输入第一个整数："))
    ib = int(input("请输入第二个整数："))
    p = ia * ib
    while (ic := ia % ib) != 0:
        ia = ib
        ib = ic
    print(f"最大公约数为 {ib}")
    print(f"最小公倍数为 {int(p / ib)}")


def question15():
    ans = a = int(input("请输入a："))
    callist = [str(a)]
    for i in range(2, int(input("请输入n：")) + 1):
        ans += a * (10**i - 1) // 9
        callist.append(str(a * (10**i - 1) // 9))
    print(f"{' + '.join(callist)} = {ans}")
