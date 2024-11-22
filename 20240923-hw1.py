def question1():
    str = "Hello World!"
    print(str)


def question2():
    str1 = "Hello World!"
    str2 = "我还是从前那个少年！"
    print(str1, str2, sep="\n")


def question3():
    a = input("Enter a string of text: ")
    print(f"What you just entered is: {a}")


def question4():
    i = int(input("Input a integer: "))
    print(f"The numerical value is {i}")
    print(f"The type is {type(i)}")


def question5():
    n = input("Input a name: ")
    print(f"{n}: Cross the stars over the moon to meet your better self.")


def question6():
    f = input("请输入一个浮点小数：")
    print(f"The result is {int(float(f))}.")


def question7():
    dp5f = input("Enter a floating point number (5 decimal places): ")
    print("The result is %.2f" % float(dp5f))


def question8():
    import math

    r = float(input("输入圆锥体的半径："))
    h = float(input("输入圆锥体的高："))
    print(f"圆锥体的半径为：{r}")
    print(f"圆锥体的高为：{h}")
    print(f"圆锥体的体积为：{(math.pi*h*math.pow(r,2))/3}")


question1()
question2()
question3()
question4()
question5()
question6()
question7()
question8()
