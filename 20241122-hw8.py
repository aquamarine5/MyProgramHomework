from typing import List, Optional

def question1():
    class Triangle:
        def __init__(self,a,b,c):
            self.a=a
            self.b=b
            self.c=c
        def judge(self)->bool:
            if self.a+self.b>self.c and self.a+self.c>self.b and self.b+self.c>self.a:
                return True
            else:
                return False
        def girth(self):
            return self.a+self.b+self.c
        def display(self):
            return f"三角形的三边为：{self.a}、{self.b}、{self.c}\n三角形的周长为{self.girth()}"
    t=Triangle(*[float(i) for i in [input(f"请输入三角形的的第{k}条边：") for k in ['一','二','三']]])
    while(not t.judge()):
        print("*"*20)
        print("输入的三边无法构成三角形，请重新输入：")
        t=Triangle(*[float(i) for i in [input(f"请输入三角形的的第{k}：") for k in ['一','二','三']]])
    print("="*20)
    print(t.display())
    print("="*20)
    
def question2():
    class Student:
        def __init__(self,id:int,name:str,age:int,score:Optional[List[float]]):
            self.name=name
            self.age=age
            self.score=score
            self.id=id
        def __str__(self):
            return '\n'.join([
                "="*20,
                f"学生信息如下：",
                f"学号：{self.id}",
                f"姓名：{self.name}",
                f"年龄：{self.age}",
                f"成绩：{self.score if self.score!=None else '无'}",
                f"平均成绩：{self._calculate_average() if self.score!=None else '无'}"
            ])
        def _calculate_average(self):
            return sum(self.score)/len(self.score)
    s=Student(input("请输入学号："),input("请输入姓名："),int(input("请输入年龄：")),None if (iscore:=input("请输入成绩，以空格分隔："))=="" else list(map(float,iscore.split())))
    print("="*20)
    print(s)
    print("="*20)
    
def question3():
    class Time:
        def __init__(self,year:int,month:int,day:int):
            self.year=year
            self.month=month
            self.day=day
        def leapyear(self)->bool:
            return (self.year%4==0 and self.year%100!=0) or self.year%400==0
        def judge(self)->bool:
            if self.month in [1,3,5,7,8,10,12]:
                return self.day<=31
            elif self.month in [4,6,9,11]:
                return self.day<=30
            elif self.month==2:
                return self.day<=29 if self.leapyear() else self.day<=28
            else:
                return False
        def __str__(self):
            return f"   {self.year}-{self.month}-{self.day}"
    t=Time(int(input("请输入年份：")),int(input("请输入月份：")),int(input("请输入日期：")))
    while(not t.judge()):
        print("*"*20)
        print("输入的日期有误，请重新输入！")
        t=Time(int(input("请输入年份：")),int(input("请输入月份：")),int(input("请输入日期：")))
    print("="*20)
    print(t)
    print("="*20)

def question4():
    class Shape:
        def perimeter(self):
            raise NotImplementedError("This method should be implemented in subclass")
        def display(self):
            raise NotImplementedError("This method should be implemented in subclass")
    class Rectangle(Shape):
        def __init__(self):
            self.length=float(input("请输入长："))
            self.width=float(input("请输入宽："))
            print("矩形创建完毕！")
        def perimeter(self)->float:
            return 2*(self.length+self.width)
        def display(self)->str:
            return f"矩形，周长为{self.perimeter():.2f}"
    class Circle(Shape):
        def __init__(self):
            self.radius=float(input("请输入半径："))
            print("圆形创建完毕！")
        def perimeter(self)->float:
            import math
            return 2*math.pi*self.radius
        def display(self)->str:
            return f"圆形，周长为{self.perimeter():.2f}"
    class Triangle(Shape):
        def __init__(self):
            self.a=float(input("请输入第一条边："))
            self.b=float(input("请输入第二条边："))
            self.c=float(input("请输入第三条边："))
            print("三角形创建完毕！")
        def perimeter(self)->float:
            return self.a+self.b+self.c
        def display(self)->str:
            return f"三角形，周长为{self.perimeter():.2f}"
    shapelist:List[Shape]=[]
    while((method:=input('\n'.join([
        "*"*20,
        "  1. 创建圆形实例",
        "  2. 创建矩形实例",
        "  3. 创建三角形实例",
        "  0. 创建完毕",
        "*"*20,
        "输入功能号："
    ])))!='0'):
        if method=='1':
            shapelist.append(Circle())
        elif method=='2':
            shapelist.append(Rectangle())
        elif method=='3':
            shapelist.append(Triangle())
    print("="*20)
    print(f"您一共创建了{len(shapelist)}个形状实例：")
    for index,shape in enumerate(shapelist):
        print(f"{index+1}. {shape.display()}")
    print("="*20)
    print(f"这些性状实例的周长总和为{sum([i.perimeter() for i in shapelist]):.2f}")
    
def question5():
    class Point():
        def __init__(self):
            self.x=float(input("----请输入x坐标："))
            self.y=float(input("----请输入y坐标："))
        def area(self):
            raise NotImplementedError("This method should be implemented in subclass")
        def display(self):
            raise NotImplementedError("This method should be implemented in subclass")
    class Rectangle(Point):
        def __init__(self):
            print("请输入矩形左上角坐标")
            super().__init__()
            self.length=float(input("请输入长："))
            self.width=float(input("请输入宽："))
            print("矩形创建完毕！")
        def area(self)->float:
            import math
            return math.abs(self.length-self.x)*math.abs(self.width-self.y)
        def display(self)->str:
            return '\n'.join([
                "="*20,
                "这是一个矩形。"
                f"左上角坐标为[{self.x},{self.y}]",
                f"矩形的长：{self.length}",
                f"矩形的宽：{self.width}",
                f"矩形的面积：{self.area():.2f}"
            ])
    class Circle(Point):
        def __init__(self):
            print("请输入圆心坐标")
            super().__init__()
            self.radius=float(input("请输入半径："))
            print("圆创建完毕！")
        def area(self)->float:
            import math
            return math.pi*self.radius**2
        def display(self)->str:
            return '\n'.join([
                "="*20,
                "这是一个圆。"
                f"圆心坐标为[{self.x},{self.y}]",
                f"圆的半径：{self.radius}",
                f"圆的面积：{self.area():.2f}",
            ])
    shapelist:List[Point]=[]
    while((method:=input('\n'.join([
        "*"*20,
        "  1. 创建圆形实例",
        "  2. 创建矩形实例",
        "  0. 创建完毕",
        "*"*20,
        "输入功能号："
    ])))!='0'):
        if method=='1':
            shapelist.append(Circle())
        elif method=='2':
            shapelist.append(Rectangle())
    for shape in shapelist:
        print(shape.display())

if __name__=="__main__":
    question1()
    question2()
    question3()
    question4()
    question5()