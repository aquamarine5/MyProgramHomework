def topic1():
    with open('file1.txt','r',encoding='gbk') as f:
        content=f.read()
        print(f"文件中包含的字符数为{len(content)}，行数为{content.count('\n')}")
        
def topic2():
    with open('file1.txt','r',encoding='gbk') as f:
        with open('file2.txt','w+',encoding='utf-8') as f2:
            f2.write("\n".join(f.read().split('\n')[::-1]))
            
def topic3():
    with open("scores.txt","r",encoding="gbk") as f:
        with open("scored.txt","w+",encoding="utf-8") as f2:
            data=["   考号      总成绩"]
            f.readline()
            for line in f.readlines():
                columnData=line.split()
                data.append(f"{columnData[0]} {int(columnData[1])*0.4+int(columnData[2])*0.6:.2f}")
            f2.write("\n".join(data))
def topic4():
    import wordcloud
    with open('4-4.txt','r',encoding="gb2312") as f:
        content=f.read()
        wc=wordcloud.WordCloud(font_path='msyh.ttc',width=800,height=600,background_color='white',max_words=10).generate(content)
        wc.to_image().save('4-4.png')
        wf=wc.process_text(content)
        most_common_words = sorted(wf.items(), key=lambda item: item[1], reverse=True)[:5]
        with open('4-4result.txt','w+',encoding="utf-8") as f:
            f.write("单词 次数\n")
            for word, freq in most_common_words:
                f.write(f"{word} {freq}\n")
                
def topic5():
    import jieba
    import wordcloud
    with open('4-5.txt','r') as f:
        content=f.read().replace('\n','')
        words=jieba.lcut(content)
        word_freq = {}
        for word in words:
            if word in ['，','。','、','：','“','”','《','》','（','）','！','？','；',' ']: continue
            word_freq[word] = word_freq.get(word, 0) + 1
        with open('4-5result.txt','w+',encoding="utf-8") as f:
            f.write("单词 次数\n")
            for word, freq in sorted(word_freq.items(), key=lambda item: item[1], reverse=True)[:10]:
                f.write(f"{word} {freq}\n")
        wordcloud = wordcloud.WordCloud(font_path='msyh.ttc', width=800, height=400, background_color='white',max_words=10).generate_from_frequencies(word_freq)
        wordcloud.to_image().save('4-5.png')
        
topic1()
topic2()
topic3()
topic4()
topic5()
