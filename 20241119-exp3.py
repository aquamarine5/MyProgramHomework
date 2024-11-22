def question1():
    print(f"{''.join([c for c in input('Please input a number and output all bits take out the even number: ') if int(c)%2==0])}")
    
def question2():
    def fun(n:int)->bool:
        return n%3==0 and n%5!=0
    print(f"{[n for n in range(100,int(input('Please input a number to calculate all the numbers meet the requirement: '))) if fun(n)]}")
    
def question3():
    def isprime(n:int)->bool:
        if n<2: return False
        for i in range(2,n):
            if n%i==0:
                return False
        return True
    def sumx(n:int)->int:
        return sum([i for i in range(2,n) if isprime(i)])
    print(f"{sumx(int(input('Please input a number to calculate the sum of prime numbers: ')))}")

def question4():
    def ave(l:list)->float:
        return sum(l)/len(l)
    print(f"平均值为：{ave([float(i) for i in input('请输入逗号分隔的若干浮点数：').split(',')]):.4f}")

def question5():
    def k(n:int)->int:
        if n==0: return 1
        if n==1: return 2
        return k(n-1)**2+k(n-2)**2
    print(f"{k(int(input("Please input a number to calculate the result: ")))}") 
    
question1()
question2()
question3()
question4()
question5()