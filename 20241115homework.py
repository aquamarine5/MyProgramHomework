from typing import List


def topic1():
    while(n:=input("Please enter an positive integer:"))!="":
        print(f"小于{n}的斐波那契数列如下：")
        a,b,c=0,1,0
        while b<int(n):
            print(f"{b:05d}",end='  ')
            a,b=b,a+b
            c+=1
            if(c%5==0):
                print('\n')
        print("\n")

def topic2(ls:List[int])->int:
    sls=sorted(ls)
    if(len(ls)%2==0):
        return (sls[len(ls)//2-1]+sls[len(ls)//2])/2
    else:
        return sls[len(ls)//2]
    
def topic3(*months):
    data=[200,388,123,456,987,342,767,234,124,345,123,234]
    return sum([data[i-1] for i in months])/len(months)

def topic4(name,/,city=None,gender=None,job=None):
    print(f"The information of {name} is: ")
    if(city!=None):
        print(f"city: {city}")
    if(gender!=None):
        print(f"gender: {gender}")
    if(job!=None):
        print(f"job: {job}")
        
def topic5():
    while(n:=input("="*20+"\n请输入逗号分隔的若干整数："))!="":
        nl=list(map(int,n.split(',')))
        print(f"最大值是{max(nl)}，最小值是{min(nl)}，和是{sum(nl)}")

def topic6():
    def cinput(argname:str)->int:
        n=input(f"Please input {argname}:")
        if not n.isdigit() or (r:=int(n))<0:
            print("Input error!")
            return cinput(argname)
        return r
    a=cinput("a")
    n=cinput("n")
    pn=[str(a)*i for i in range(1,n+1)]
    print(f"{' + '.join(pn)} = {sum(map(int,pn))}")
    
def topic7():
    while(n:=input("Please input the num: "))!="":
        if not n.isdigit():
            continue
        rn=int(n)
        pn=[str(k) for k in range(1,rn) if rn%k==0]
        rrm={
            '=':'a complete',
            '<':'an insufficient',
            '>':'an abundant'
        }
        print(f"{'+'.join(pn)}{(rd:=('=' if (sn:=sum(map(int,pn)))==rn else '<' if sn<rn else '>'))}{rn}, is {rrm[rd]} number.")
        
def topic8():
    while(n:=input("Please input the num: "))!="":
        if(len(n)!=3):
            continue
        if int(n) == sum([int(digit) ** 3 for digit in n]):
            print(f"{n} is a Narcissus number.")
        else:
            print(f"{n} is not a Narcissus number.")
            
def topic9():
    while(n:=int(input("Please input an even number(2-8, press '0' for exit): ")))!=0:
        if not 2<=n<=8:
            print("Out of the range.")
        else:
            print((n+1)**n-n**(n-1))
            
def topic10():
    while(n:=input("请输入测试密码（直接回车为退出）："))!="":
        sl=[0,0,0,0]
        for c in n:
            if 97<=ord(c)<=122:
                sl[2]=1
            if 65<=ord(c)<=90:
                sl[1]=1
            if 48<=ord(c)<=57:
                sl[0]=1
        if(len(n)>=8): sl[3]=1
        print(f"{n}的密码强度为{sum(sl)}级")

def topic11():
    while(n:=input("Please enter an integer: "))!="":
        if not n.isdigit() or int(n)<0:
            print("Input error!")
            continue
        print(f"The converted number is {''.join(sorted(n,reverse=True))}")
        
topic1()
print(topic2([26,92,-5,13,6]))
print(topic2([26,92,-5,13,6,117,-25,73]))
print(topic3(1,2,3,4,5,6,7))
topic4("Tom",city="Shanghai",gender="M")
topic5()
topic6()
topic7()
topic8()
topic9()
topic10()
topic11()