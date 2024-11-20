def question1():
    print(f"{[c for c in input() if int(c)%2==0]}")
    
def question2():
    def fun(n:int)->bool:
        return n%3==0 and n%5!=0
    print(f"{[n for n in range(100,int(input())) if fun(n)]}")
    
def question3():
    def isprime(n:int)->bool:
        if n<2: return False
        for i in range(2,n):
            if n%i==0:
                return False
        return True
    def sum(n:int)->int:
        return sum([i for i in range(2,n) if isprime(i)])
    print(f"{sum(int(input()))}")

def question4():
    def ave(l:list)->float:
        return sum(l)/len(l)
    print(f"{ave([float(i) for i in input().split(',')])}")

def question5():
    def k(n:int)->int:
        if n==0: return 1
        if n==1: return 2
        return k(n-1)**2+k(n-2)**2
    print(f"{k(int(input()))}") 