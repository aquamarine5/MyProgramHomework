import sys,ast

def f1():
    def getnumber(n):
        a=input(f"Input the {n} number: ")
        try:
            b=ast.literal_eval(a)
            if(type(b)!=int):
                print(f"ERROR: {a} is not a number!")
                sys.exit()
        except:
            print(f"ERROR: {a} can not be eval.")
            sys.exit()
        return b
    a=getnumber("first")
    o=input("Input the operater(+, -, *, / are legal): ")
    if(o not in ['+','-','*','/']):
        print(f'ERROR: {o} is a illegal operater.')
        sys.exit()
    b=getnumber("second")
    if(o=='/' and b==0):
        print('ERROR: 0 can not be divided.')
        sys.exit()
    print(f"The result is {ast.literal_eval(f'{a}{o}{b}')}")

def f2():
    n=0
    for i in range(1,101):
        n+=i*-(-1)**i
    print(n)
    
def f3():
    t=[]
    for i in range(1,500):
        if(i%3==0 and i%7==0):
            t.append(i)
        if(len(t)==8):
            print(' '.join([str(n).rjust(3,'0') for n in t]))
            t=[]
    if(len(t)!=0):
        print(' '.join([str(n).rjust(3,'0') for n in t]))
            
f3()