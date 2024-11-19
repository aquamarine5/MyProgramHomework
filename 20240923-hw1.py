def topic1():
    str="Hello World!"
    print(str)
def topic2():
    str1="Hello World!"
    str2="我还是从前那个少年！"
    print(str1,str2,sep="\n")
def topic3():
    a=input("Enter a string of text: ")
    print(f"What you just entered is: {a}")
def topic4():
    i=int(input("Input a integer: "))
    print(f"The numerical value is {i}")
    print(f"The type is {type(i)}")
def topic5():
    n=input("Input a name: ")
    print(f"{n}: Cross the stars over the moon to meet your better self.")
def topic6():
    f=input("请输入一个浮点小数：")
    print(f"The result is {int(float(f))}.")
def topic7():
    dp5f=input("Enter a floating point number (5 decimal places): ")
    print("The result is %.2f"%float(dp5f))
def topic8():
    import math
    r=float(input("输入圆锥体的半径："))
    h=float(input("输入圆锥体的高："))
    print(f"圆锥体的半径为：{r}")
    print(f"圆锥体的高为：{h}")
    print(f"圆锥体的体积为：{(math.pi*h*math.pow(r,2))/3}")

topic1()
topic2()
topic3()
topic4()
topic5()
topic6()
topic7()
topic8()
