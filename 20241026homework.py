def topic1():
    print(f"{123456:+>25}")

def topic2():
    print(f"{12345678.9:>30,}")
    
def topic3():
    print(f"二进制形式：{0x1010:#b}")
    print(f"八进制形式：{0x1010:#o}")
    print(f"十进制形式：{0x1010:d}")
    print(f"十六进制形式：{0x1010:#x}")
    
def topic4():
    print(f"逆序之后的整数为{input('请输入正整数：')[::-1]}")
    
def topic5():
    print(f"全部转小写之后的字符串为：{input('输入字符串：').lower()}")
    
def topic6():
    print(f"字符a出现了{input('请输入一个字符串：').count('a')}次。")
    
def topic7():
    print(f"数列中最大的值是{max(int(n) for n in input('输入一组数字，采用逗号分隔: ').split(','))}。")
    
def topic8():
    print(f'列表中的数值型数据为：{" ".join(numlist:=[str(element) for element in [123.5, "456", "Lucy", 789, "hello", "123", 456, "789"] if isinstance(element,(int,float))])}')
    print(f'这些数值的和是{sum([eval(element) for element in numlist])}。')

def topic9():
    print(f"{'hello_world_yoyo'.split('_')}")

def topic10():
    print(f"{'_'.join(["hello", "world", "yoyo"])}")
    
def topic11():
    print(f"{input('请输入一个字符串：').replace(' ',r'%20')}")
    
def topic12():
    (listA := ['水煮干丝','平桥豆腐','白灼虾','香菇青菜','西红柿鸡蛋汤']).append("红烧肉")
    listA.remove("水煮干丝")
    print(listA)
    
def topic13():
    ss=[*dict.fromkeys(s:=input("请输入一个字符串："))]
    citer=int(input(f'第几个只出现{(count:=int(input("字符出现的次数：")))}次的字符：'))
    print('='*20,f'第{citer}个只出现{count}次的字符是{ss[[i for i,v in enumerate([s.count(char) for char in ss]) if v==count][citer-1]]}',"="*20,sep="\n")
    
def topic14():
    print(f"'{word}'在字符串'{message}'中出现了{count}次" if (count:=(message:=input('请输入一个字符串：')).count(word:=input('请输入要查找的字符串：'))) else f"'{word}'不在字符串'{message}'中。")
    
def topic15():
    import datetime
    year=int(input('请输入年份：'))
    print(f"{year} 年是{'闰' if (year%4==0 and year%100!=0) or year%400==0 else '平'}年")
    print(f"{year} 年 {(month:=int(input('请输入月份：')))} 月 {(day:=int(input('请输入日期：')))} 日是当年的第 {datetime.datetime(year,month,day).timetuple().tm_yday} 天")
    
def topic16():
    print(f"原始数列：{(rdata:=input('请输入空格分隔的若干个整数：'))}")
    sdata=sorted([int(element) for element in rdata.split(" ")])
    deltavalue=min((delta:=[sdata[i]-sdata[i-1] for i in range(len(sdata)-1,0,-1)]))
    print(f"最接近数是 {sdata[(index:=(len(delta)-1-delta.index(deltavalue)))]} 和 {sdata[index+1]} ,它们的差值是 {deltavalue}。")
    
def topic17():
    num= snum if len(snum:=input("请输入一个大整数: "))%2==0 else "0"+snum
    print(f"{snum} {'' if sum([int(num[i:i+1]) for i in range(0,len(num),2)])%11==0 else '不'}能被 11 整除！")
    
def topic18():
    print(f"删除重复的元素之前的列表为：{(rl:=[int(element) for element in input('请输入空格分隔的若干个整数：').split(' ')])}")
    print(f"删除重复的元素之后的列表为：{[*dict.fromkeys(rl)]}")
    
def topic19():
    print(f"调整之前的列表为：{(rl:=[int(element) for element in input('请输入空格分隔的若干个整数：').split(' ')])}")
    print(f"调整之后的列表为：{[jn for jn in rl if jn%2==1]+[on for on in rl if on%2==0]}")
    
def topic20():
    croplist=(rnl:=input('请输入逗号分隔的若干个整数：').split(','))[:(pos:=int(input('请输入左移位数：')))-1]
    print(f"原始数列：{' '.join(rnl)}")
    print(f"左移{pos}位后的数列：{' '.join(rnl[pos-1:]+croplist)}")
    
def topic21():
    values = [8,9,5,10,8,6,8,7,9,9.5]
    print(f"原始分数：{' '.join([str(score) for score in values])}")
    print(f"去掉一个最低分、一个最高分之后：{' '.join(afterscore:=[str(es) for es in values if es!=max(values) and es!=min(values)])}")
    print(f"该歌手的最后得分为 {sum([eval(ias) for ias in afterscore])/len(afterscore):.2f}")
    
def topic22():
    wordlist=input('请输入空格分隔的若干个单词：').split(' ')
    print(f"最长的单词长度为 {(ml:=max([len(word) for word in wordlist]))}: {' '.join([mlword for mlword in wordlist if len(mlword)==ml])}")
    
def topic23():
    print(f"You have spent a total of {sum({'卡布奇洛': 32, '摩卡': 30, '抹茶蛋糕': 28, '布朗尼': 26}.values())} yuan.")
    
def topic24():
    fruits = {"apple":10,"mango":12,"durian":20,"banana":5}
    print(f"最贵的水果是 {[*fruits.keys()][[*fruits.values()].index(price:=(max(fruits.values())))]}，价格为 {price}。")
    
def topic25():
    string=input('请输入一个字符串：')
    print(f"LETTERS: {len([letter for letter in string if letter.isalpha()])}")
    print(f"DIGITS: {len([letter for letter in string if letter.isdigit()])}")
    
def topic26():
    (studs := [{'sid': '103', 'Chinese': 90, 'Math': 92, 'English': 91},{'sid': '101', 'Chinese': 87, 'Math': 90, 'English': 82},{'sid': '102', 'Chinese': 76, 'Math': 77, 'English': 73}]).sort(key=lambda stud:int(stud['sid']))
    print(*[f'{stud["sid"]}: {[stud["Chinese"],stud["Math"],stud["English"]]}' for stud in studs],sep="\n")
    