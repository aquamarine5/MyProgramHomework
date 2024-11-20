def question1():
    print(f"{','.join([str(i) for i in range(2000,3200) if i%7==0 and i%5!=0])}")
    
def question2():
    print(f'{",".join(sorted(input("请输入一个字符串：").split(",")))}')
    
def question3():
    print(f"{input('请输入一个字符串：').upper()}")
    
def question4():
    print(f"{' '.join(sorted([*{*input('请输入一个字符串：').split(' ')}]))}")

def question5():
    print(f"{','.join([i for i in input().split(',') if int(i)%2!=0])}")
    
def question6():
    data=[11,22,33,44,55,66,77,88,99,90]
    print({'k1':[i for i in data if i <66],'k2':[j for j in data if j>66]})

def question7():
    nums=[2, 7, 11, 15, 1, 8]
    print([(nums[i],nums[j]) for i in range(len(nums)) for j in range(i+1,len(nums)) if nums[i]+nums[j]==9])
    
def question8():
    current=['手机','电脑','鼠标垫','游艇']
    while((m:=int(input('\n'.join(['*'*20,f'现有商品：{current}','*'*20,'1.添加商品','2.查询商品','0.退出','请输入功能号：']))))!=0):
        if(m==1):
            current.append(input('请输入要添加的商品名称：'))
        elif m==2:
            print(f"{current[int(input('请输入商品序号：'))]}")
        else:
            print("序号输入错误！")

def question9():
    money=int(input('请输入你的总资产：'))
    while((m:=int(input('\n'.join(['*'*20,str((items:={1:'电脑',2:'鼠标',3:'台灯',4:'自行车'})),'*'*20,'','请输入你想要购买的商品序号（按数字0结束）：']))))!=0):
        if m in items:
            price={1:3500,2:40,3:998,4:998}[m]
            print(f'你想要购买的是：{items[m]}',f'它的价格是：{price}',sep='\n')
            if money>=price:
                money-=price
                print(f"购买成功！   余额：{money}")
            else:
                print(f"余额不足！请速去充值！    余额：{money}")
        else:
            print("商品不存在！")

def question10():
    hashlist=[ 'g', 'K', 'a', 'P', 'W', 'x', 'E', 'Q', 'f', 't']
    print(f"The Plaintext is: {''.join([str(hashlist.index(c)) if c in hashlist else '?' for c in input('Please input the ciphertext(\'q\' for Exit):')])}")
    
def question11():
    cardNums=input('请输入卡号：')
    print('合法' if 10-min([int(x) for x in list(str(sum([sum([int(p) for p in str(int(n)*2)]) for n in cardNums[:-1:2]])+sum([int(n) for n in cardNums[1:-1:2]])))])==int(cardNums[-1]) else '不合法')
    
question1()
question2()
question3()
question4()
question5()
question6()
question7()
question8()
question9()
question10()
question11()