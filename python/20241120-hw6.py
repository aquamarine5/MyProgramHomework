"""
Author: aquamarine5 && aquamarine5_@outlook.com
Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
"""

import tkinter as tk

# Enabled High DPI awareness for Windows 10/11
try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


def question1():
    rw = tk.Tk()
    rw.title("Question 1")
    rw.geometry("300x200")
    entryframe = tk.Frame(rw)
    entryframe.pack(pady=20)
    entry1 = tk.Entry(entryframe, width=10)
    entry1.pack(side=tk.LEFT, padx=8)
    entry2 = tk.Entry(entryframe, width=10)
    entry2.pack(side=tk.LEFT, padx=8)
    btnframe = tk.Frame(rw)
    btnframe.pack(pady=10)

    def add_callback():
        textbox.insert(
            tk.END,
            entry1.get()
            + "+"
            + entry2.get()
            + "="
            + str(float(entry1.get()) + float(entry2.get()))
            + "\n",
        )

    btnadd = tk.Button(btnframe, text="加法", command=add_callback, width=9)
    btnadd.pack(side=tk.LEFT, padx=8)

    def clear_callback():
        textbox.delete(1.0, tk.END)

    btnclear = tk.Button(btnframe, text="清空", command=clear_callback, width=9)
    btnclear.pack(side=tk.LEFT, padx=8)
    textbox = tk.Text(rw, height=10, width=25)
    textbox.pack(pady=8)
    rw.mainloop()


def question2():
    rw = tk.Tk()
    rw.title("Question 2")
    rw.geometry("300x300")
    entryframe = tk.Frame(rw)
    entryframe.pack(pady=20)
    entry1var = tk.StringVar()
    entry2var = tk.StringVar()
    entry1 = tk.Entry(entryframe, textvariable=entry1var, width=10)
    entry1.pack(side=tk.LEFT, padx=8)
    entry2 = tk.Entry(entryframe, textvariable=entry2var, width=10)
    entry2.pack(side=tk.LEFT, padx=8)
    radiovar = tk.StringVar(value="operation")

    def calculateValue(*args):
        if radiovar.get() == "加上":
            result = float(entry1.get()) + float(entry2.get())
        elif radiovar.get() == "减去":
            result = float(entry1.get()) - float(entry2.get())
        elif radiovar.get() == "乘以":
            result = float(entry1.get()) * float(entry2.get())
        elif radiovar.get() == "除以":
            result = float(entry1.get()) / float(entry2.get())
        else:
            return
        textbox.config(
            text=f"{entry1.get()}{radiovar.get()}{entry2.get()}等于{result:.2f}\n"
        )

    entry1var.trace_add("write", calculateValue)
    entry2var.trace_add("write", calculateValue)
    radiovar.trace_add("write", calculateValue)
    radioframe = tk.Frame(rw)
    radioframe.pack(pady=10)
    radioplus = tk.Radiobutton(radioframe, text="加", variable=radiovar, value="加上")
    radioplus.pack(side=tk.TOP, pady=2)
    radiominus = tk.Radiobutton(radioframe, text="減", variable=radiovar, value="减去")
    radiominus.pack(side=tk.TOP, pady=2)
    radiomul = tk.Radiobutton(radioframe, text="乘", variable=radiovar, value="乘以")
    radiomul.pack(side=tk.TOP, pady=2)
    radiodiv = tk.Radiobutton(radioframe, text="除", variable=radiovar, value="除以")
    radiodiv.pack(side=tk.TOP, pady=2)
    textbox = tk.Label(rw, height=10, width=25)
    textbox.pack(pady=8)
    rw.mainloop()


def question3():
    rw = tk.Tk()
    rw.title("Question 3")
    rw.geometry("300x200")
    inputEntry = tk.Entry(rw, width=30)
    inputEntry.pack(pady=3)

    def check():
        # ref: https://zhuanlan.zhihu.com/p/44190338
        def check_builtin(id: str) -> bool:
            if len(id) != 18 or not id[:-1].isdigit():
                return False
            if not (id[-1].isdigit() or id[-1] == "X" or id[-1] == "x"):
                return False
            weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            checkcodes = "10X98765432"
            total = sum(int(id[i]) * weights[i] for i in range(17))
            return checkcodes[total % 11] == id[-1]

        if check_builtin(inputEntry.get()):
            resultLabel.config(text="为合法号码")
        else:
            resultLabel.config(text="为非法号码")

    checkbtn = tk.Button(rw, text="校验", command=check)
    checkbtn.pack(anchor="e", padx=10)
    resultLabel = tk.Label(rw, width=20)
    resultLabel.pack(pady=10, anchor="w")
    rw.mainloop()


def question4():
    rw = tk.Tk()
    rw.title("Question 4")
    rw.geometry("600x600")
    selectlabel = tk.Label(rw, text="请选择景点：")
    selectlabel.pack(pady=5)
    posvar = tk.StringVar(value="nothing")
    pearlradiobtn = tk.Radiobutton(
        rw, text="东方明珠", variable=posvar, value="东方明珠"
    )
    pearlradiobtn.pack(pady=5)
    zooradiobtn = tk.Radiobutton(rw, text="动物园", variable=posvar, value="动物园")
    zooradiobtn.pack(pady=5)
    techradiobtn = tk.Radiobutton(rw, text="科技馆", variable=posvar, value="科技馆")
    techradiobtn.pack(pady=5)
    ticketlabel = tk.Label(rw, text="请输入购票张数：")
    ticketlabel.pack(pady=5)
    ticketentry = tk.Entry(rw)
    ticketentry.pack(pady=5)
    priceMap: dict[str, int] = {"东方明珠": 160, "动物园": 130, "科技馆": 60}

    def calculatePrice():
        resulttext.insert(
            tk.END,
            f"购{(cpos:=posvar.get())}票{(ticketcount:=int(ticketentry.get()))}张，票价{priceMap[cpos]*ticketcount*(0.8 if ticketcount>50 else 0.95 if ticketcount>20 else 1):.2f}元\n",
        )

    calculatebtn = tk.Button(rw, text="计算", width=10, command=calculatePrice)
    calculatebtn.pack(pady=5)
    resulttext = tk.Text(rw, height=40, width=40)
    resulttext.pack(fill=tk.BOTH)
    rw.mainloop()


question1()
question2()
question3()
question4()
