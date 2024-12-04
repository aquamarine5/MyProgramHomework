"""
Author: aquamarine5 && aquamarine5_@outlook.com
Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
Seealso: https://github.com/aquamarine5/MyProgramHomework/blob/main/20241123-final.py.
License: AGPLv3.
Produced by human, not by AI, although some code may be co-completed by Github Copilot.
Only used for the final homework of the class of Python at Hebei University (HBU).
Try to find out the funny point of the code. :)
Code version: v6, 2024-12-02.
Comment version: v3, 2024-12-02.
"""

import datetime
import json
import re
import os
import random
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser, filedialog, messagebox
import tkinter.font
from typing import List, Optional
import urllib.request
import urllib.error

# 默认的课程表数据文件存储路径
DEFAULT_TIMETABLE_JSON_PATH = "timetable.json"


class TimetableClassTime:
    """课程持续时间"""

    def __init__(self, startTime: int, endTime: int):
        self.startTime = startTime
        self.endTime = endTime


class TimetableClassWeekTime:
    """课程起始周和结束周"""

    def __init__(self, startWeek: int, endWeek: int):
        self.startWeek = startWeek
        self.endWeek = endWeek


class TimetableColumnTime:
    """课程表时间段"""

    def __init__(self, startTime: str, endTime: str):
        self.startTime = startTime
        self.endTime = endTime


class TimetableClassPosition:
    """单个课程的位置"""

    def __init__(self, cid: int, time: TimetableClassTime):
        self.id = cid
        self.time = time


class TimetableClassIdentity:
    """课程信息"""

    def __init__(
        self,
        name: str,
        teacher: Optional[str],
        location: Optional[str],
        weekTime: Optional[TimetableClassWeekTime],
        color: str,
    ):
        self.name = name
        self.color = color
        self.teacher = teacher
        self.location = location
        self.weekTime = weekTime


class Timetable:
    """课表数据"""

    def __init__(
        self,
        classes: List[List[TimetableClassPosition]],
        classids: List[TimetableClassIdentity],
        columnTimes: List[TimetableColumnTime],
        name: str,
        istemplated: bool = False,
    ):
        self.classes = classes
        self.columnTimes = columnTimes
        self.name = name
        self.classids = classids
        self.istemplated = istemplated

    def addClassId(self, cid: TimetableClassIdentity) -> int:
        """添加一个新的课程信息，并返回其对于的数字ID"""
        self.classids.append(cid)
        return len(self.classids) - 1

    @staticmethod
    def createBlankTimetable() -> "Timetable":
        return Timetable(
            [[[] for _ in range(7)] for _ in range(11)], [], [], "新建课程表", True
        )

    @staticmethod
    def createHBUTemplatedTimetable() -> "Timetable":
        return Timetable(
            [[[] for _ in range(7)] for _ in range(11)],
            [],
            [
                TimetableColumnTime("08:00", "08:45"),
                TimetableColumnTime("08:55", "09:40"),
                TimetableColumnTime("10:10", "10:55"),
                TimetableColumnTime("11:05", "11:50"),
                TimetableColumnTime("14:30", "15:15"),
                TimetableColumnTime("15:25", "16:10"),
                TimetableColumnTime("16:20", "17:05"),
                TimetableColumnTime("17:15", "18:00"),
                TimetableColumnTime("19:00", "19:45"),
                TimetableColumnTime("19:55", "20:40"),
                TimetableColumnTime("20:50", "21:35"),
            ],
            "河北大学课程表",
            True,
        )

    def saveToJSON(self, filepath: str = DEFAULT_TIMETABLE_JSON_PATH):
        """将课程表数据保存到JSON文件\n
        请注意 timetable.json 并不是一个合法的JSON文件，因为它使用回车符进行数据分隔，这一点有点像CSV格式的JSON文件，目的是为了与WakeUp课程表的导入数据互适配。
        """
        c: List[str] = [
            '"v1"',
            self._parseColumnTime(),
            self._parseDetails(),
            self._parseClassId(),
            self._parseClassTime(),
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(c))
            print("TimetableSaveToJSON: ", filepath)

    def _parseDetails(self) -> str:
        return json.dumps({"tableName": self.name, "nodes": len(self.columnTimes)})

    def _parseColumnTime(self) -> str:
        return json.dumps(
            [
                {"startTime": ct.startTime, "endTime": ct.endTime}
                for ct in self.columnTimes
            ]
        )

    def _parseClassId(self) -> str:
        return json.dumps(
            [{"color": cid.color, "courseName": cid.name} for cid in self.classids]
        )

    def _parseClassTime(self) -> str:
        d: List[str] = []
        for day, week in enumerate(self.classes):
            for ct in week:
                if ct == []:
                    continue
                cid = self.classids[ct.id]
                d.append(
                    {
                        "day": day + 1,
                        "startNode": ct.time.startTime,
                        "step": ct.time.endTime - ct.time.startTime + 1,
                        "id": ct.id,
                        "room": cid.location,
                        "teacher": cid.teacher,
                        "startWeek": cid.weekTime.startWeek,
                        "endWeek": cid.weekTime.endWeek,
                    }
                )
        return json.dumps(d)


class TimetableImporterInterface:
    def __init__(self):
        raise NotImplementedError("This is an interface class")

    def getTimetable(self) -> Timetable:
        raise NotImplementedError("This is an interface class")


class TimetableJSONImporter(TimetableImporterInterface):
    def __init__(self):
        pass

    def getTimetable(self, file: str = DEFAULT_TIMETABLE_JSON_PATH) -> Timetable:
        with open(file, "r", encoding="utf-8") as f:
            c = f.read()
            wri = TimetableWakeupRemoteImporter()
            return wri.parseByJSON(c)

    @staticmethod
    def readLocalTimetableJSONIfExisted(
        filepath: str = DEFAULT_TIMETABLE_JSON_PATH,
    ) -> Optional[Timetable]:
        if os.path.exists(filepath):
            importer = TimetableJSONImporter()
            return importer.getTimetable(filepath)
        else:
            return None


class TimetableWakeupRemoteImporter(TimetableImporterInterface):
    def __init__(self):
        pass

    def getTimetable(self, shareId: str) -> Optional[Timetable]:
        req = urllib.request.Request(
            f"https://i.wakeup.fun/share_schedule/get?key={shareId}"
        )
        req.add_header("version", "250")
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read()
                data_str = data.decode("utf-8")
                json_data = json.loads(data_str)
                print(json_data)
        except urllib.error.HTTPError as e:
            raise e
        if json_data["data"] == "":
            return None
        return self._builtinParseByJSON(json_data["data"])

    def parseByJSON(
        self, timetable_json: str, israndomcolor: bool = False
    ) -> Timetable:
        if timetable_json == "":
            raise ValueError("No timetable found")
        self.timetable_data: List[str] = timetable_json.split("\n")
        self.timetable_time = json.loads(self.timetable_data[1])
        self.timetable_details = json.loads(self.timetable_data[2])
        self.timetable_classid = json.loads(self.timetable_data[3])
        self.timetable_classtime = json.loads(self.timetable_data[4])
        self._parseBaseInformation()
        return self._parseTimetable(israndomcolor)

    def _builtinParseByJSON(self, timetable_json: str) -> Timetable:
        return self.parseByJSON(timetable_json, True)

    def _parseBaseInformation(self):
        self.timetable_name: str = self.timetable_details["tableName"]
        classtimes: List[TimetableColumnTime] = []
        for ctp in self.timetable_time[: int(self.timetable_details["nodes"])]:
            print("TimetableColumnTime.load: ", ctp)
            classtimes.append(TimetableColumnTime(ctp["startTime"], ctp["endTime"]))
        self.timetable_columntimes = classtimes

    def _parseRGBAColorToRGB(self, rgba_color: str) -> str:
        return rgba_color[:-2]

    def _parseColor(self, color: str) -> str:
        if len(color) > 7:
            return self._parseRGBAColorToRGB(color)
        else:
            return color

    def _randomColor(self) -> str:
        r = random.randint(127, 255)
        g = random.randint(127, 255)
        b = random.randint(127, 255)
        return f"#{r:02X}{g:02X}{b:02X}"

    def _parseTimetable(self, israndomcolor: bool) -> Timetable:
        ttl: List[List[TimetableClassPosition]] = [[] for _ in range(7)]
        tpl: List[TimetableClassIdentity] = []
        for clsid in self.timetable_classid:
            tpl.append(
                TimetableClassIdentity(
                    clsid["courseName"],
                    None,
                    None,
                    None,
                    (
                        self._randomColor()
                        if israndomcolor
                        else self._parseColor(clsid["color"])
                    ),
                )
            )
        for cls in self.timetable_classtime:
            ttl[cls["day"] - 1].append(
                TimetableClassPosition(
                    cls["id"],
                    TimetableClassTime(
                        cls["startNode"], cls["startNode"] + cls["step"] - 1
                    ),
                )
            )
            ctpl: TimetableClassIdentity = tpl[cls["id"]]
            ctpl.teacher = cls["teacher"]
            ctpl.location = cls["room"]
            ctpl.weekTime = TimetableClassWeekTime(cls["startWeek"], cls["endWeek"])
        return Timetable(ttl, tpl, self.timetable_columntimes, self.timetable_name)


class TimetableMainRenderer:
    def __init__(self, timeTable: Timetable):
        self.timetable = timeTable
        if self.timetable.istemplated:
            self.popupCreateNewTimetable()
            return
        self.mwin = tk.Tk()
        self.mwin.geometry("1150x950")
        self.mwin.title("课表界面")
        self.lastButton: int = -1

        lbframemain = tk.LabelFrame(self.mwin, text="课表")

        labelweeks = [
            tk.Label(lbframemain, text=weekname)
            for weekname in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        ]
        labelclasstimes = [
            tk.Label(lbframemain, text=classtimes)
            for classtimes in [
                f"{time.startTime}-{time.endTime}"
                for time in self.timetable.columnTimes
            ]
        ]
        for index, labelweek in enumerate(labelweeks):
            labelweek.grid(row=0, column=index + 1)
        for index, labelclasstime in enumerate(labelclasstimes):
            labelclasstime.grid(row=index + 1, column=0, padx=5)

        nowweekday = datetime.datetime.now().weekday()
        labelweeks[nowweekday].config(font=tkinter.font.Font(weight="bold", size=12))
        self.cvmap: List[List[int]] = [[-1 for _ in range(11)] for _ in range(7)]

        for index, cawt in enumerate(self.timetable.classes):
            for ct in cawt:
                for i in range(
                    ct.time.startTime + 1, ct.time.endTime - ct.time.startTime + 2
                ):
                    self.cvmap[index][i] = ct.id

        for i in range(7):
            for j in range(11):
                btn = tk.Button(
                    lbframemain,
                    text="无课",
                    bg="SystemButtonFace",
                    height=2,
                    width=6,
                    state=tk.DISABLED,
                )
                btn.grid(row=j + 1, column=i + 1, padx=5, pady=5)

        self.cpbtnlists: List[tk.Button] = []
        for index, cawt in enumerate(self.timetable.classes):
            for ct in cawt:
                if ct == []:
                    continue
                cid = self.timetable.classids[ct.id]
                step = ct.time.endTime - ct.time.startTime + 1
                start_col = ct.time.startTime
                iii = len(self.cpbtnlists)
                btn = tk.Button(
                    lbframemain,
                    text=cid.name,
                    bg=cid.color,
                    height=2,
                    width=6,
                    cursor="hand2",
                    wraplength=70,
                    justify=tk.CENTER,
                    command=lambda cp=ct, btn_index=iii: self.handleButtonCallback(
                        cp, btn_index
                    ),
                    borderwidth=2,
                    relief=tk.RAISED,
                )
                btn.grid(
                    row=start_col,
                    column=index + 1,
                    rowspan=step,
                    padx=5,
                    pady=5,
                    sticky="nsew",
                )
                self.cpbtnlists.append(btn)

        # *** w1 w2 w3 w4 w5 w6 w7
        # t01
        # t02
        # t03
        # t04
        # t05
        # t06
        # t07
        # t08
        # t09
        # t10
        # t11
        # lbframemain 同样通过 grid(row, column) 进行渲染。
        # 与 TimetableEditorRenderer 不同的是，他还设置了 rowspan 属性使课程按钮能够跨行显示。

        lbframemain.grid(row=0, column=0, padx=20, pady=20, rowspan=3)

        lbframedetail = tk.LabelFrame(self.mwin, text="课程详情")

        frameclassname = tk.Frame(lbframedetail)
        labelclassname = tk.Label(frameclassname, text="课程名称：")
        labelclassname.grid(row=0, column=0, padx=3, pady=3)
        self.labelvclassname = tk.Label(
            frameclassname, text="", wraplength=200, justify=tk.LEFT
        )
        self.labelvclassname.grid(row=0, column=1, padx=3, pady=3)
        frameclassname.pack(padx=20, pady=4, anchor="w")

        frameteachername = tk.Frame(lbframedetail)
        labelteachername = tk.Label(frameteachername, text="教师姓名：")
        labelteachername.grid(row=0, column=0, padx=3, pady=3)
        self.labelvteachername = tk.Label(
            frameteachername, text="", wraplength=200, justify=tk.LEFT
        )
        self.labelvteachername.grid(row=0, column=1, padx=3, pady=3)
        frameteachername.pack(padx=20, pady=4, anchor="w")

        frameroomname = tk.Frame(lbframedetail)
        labelroomname = tk.Label(frameroomname, text="教室名称：")
        labelroomname.grid(row=0, column=0, padx=3, pady=3)
        self.labelvroomname = tk.Label(
            frameroomname, text="", wraplength=200, justify=tk.LEFT
        )
        self.labelvroomname.grid(row=0, column=1, padx=3, pady=3)
        frameroomname.pack(padx=20, pady=4, anchor="w")

        frameweekstart = tk.Frame(lbframedetail)
        labelweekstart = tk.Label(frameweekstart, text="起始周：")
        labelweekstart.grid(row=0, column=0, padx=3, pady=3)
        self.labelvweekstart = tk.Label(frameweekstart, text="")
        self.labelvweekstart.grid(row=0, column=1, padx=3, pady=3)
        frameweekstart.pack(padx=20, pady=4, anchor="w")

        frameweekend = tk.Frame(lbframedetail)
        labelweekend = tk.Label(frameweekend, text="结束周：")
        labelweekend.grid(row=0, column=0, padx=3, pady=3)
        self.labelvweekend = tk.Label(frameweekend, text="")
        self.labelvweekend.grid(row=0, column=1, padx=3, pady=3)
        frameweekend.pack(padx=20, pady=4, anchor="w")

        lbframedetail.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        lbframenextclass = tk.LabelFrame(self.mwin, text="下一节课")
        nextclass: TimetableClassPosition = self.findNextClass()
        framencclassname = tk.Frame(lbframenextclass)
        labelncclassname = tk.Label(
            framencclassname, text="课程名称：", justify=tk.LEFT, wraplength=200
        )
        labelncclassname.grid(row=0, column=0, padx=3, pady=3)
        labelvncclassname = tk.Label(
            framencclassname, text=self.timetable.classids[nextclass.id].name
        )
        labelvncclassname.grid(row=0, column=1, padx=3, pady=3)
        framencclassname.pack(padx=20, pady=4, anchor="w")

        framencteachername = tk.Frame(lbframenextclass)
        labelncteachername = tk.Label(
            framencteachername, text="教师姓名：", justify=tk.LEFT, wraplength=200
        )
        labelncteachername.grid(row=0, column=0, padx=3, pady=3)
        labelvncteachername = tk.Label(
            framencteachername, text=self.timetable.classids[nextclass.id].teacher
        )
        labelvncteachername.grid(row=0, column=1, padx=3, pady=3)
        framencteachername.pack(padx=20, pady=4, anchor="w")

        framencclassroom = tk.Frame(lbframenextclass)
        labelncclassroom = tk.Label(
            framencclassroom, text="教室地点：", justify=tk.LEFT, wraplength=200
        )
        labelncclassroom.grid(row=0, column=0, padx=3, pady=3)
        labelvncclassroom = tk.Label(
            framencclassroom, text=self.timetable.classids[nextclass.id].location
        )
        labelvncclassroom.grid(row=0, column=1, padx=3, pady=3)
        framencclassroom.pack(padx=20, pady=4, anchor="w")

        lbframenextclass.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        framebtncontrol = tk.Frame(self.mwin)
        btnedit = tk.Button(framebtncontrol, text="编辑课表", command=self.showEditor)
        btnedit.grid(row=0, column=0, padx=10, pady=10)
        btnimport = tk.Button(
            framebtncontrol, text="覆盖并导入新课表", command=self.showImporterWindow
        )
        btnimport.grid(row=0, column=1, padx=10, pady=10)
        framebtncontrol.grid(row=2, column=1, padx=10, pady=10)

        self.mwin.mainloop()

    def showEditor(self):
        self.mwin.destroy()
        TimetableEditorRenderer(self.timetable)

    def findNextClass(self) -> TimetableClassPosition:
        now = datetime.datetime.now()
        todayofweek = now.weekday()
        ctime = now.hour * 60 + now.minute

        def parseTimeToMinute(time_str: str) -> int:
            h, m = map(int, time_str.split(":"))
            return h * 60 + m

        nearestclasspos = None

        # You need to know that it was a symbol of a very big number below, and you can try to chr() it to find out what it is.
        # It's a joke of the coder/ author, or a type of watermark, don't take it seriously. @aquamarine5, not generated by AI.
        mintimeandTryChrIt = (105) * (108 + 111 + 118 + 101) * (121 + 111 + 117)

        for dayofweek in range(7):
            checkday = (todayofweek + dayofweek) % 7
            dayclasses = self.timetable.classes[checkday]
            for classposition in dayclasses:
                if not classposition:
                    continue
                stime = parseTimeToMinute(
                    self.timetable.columnTimes[
                        classposition.time.startTime - 1
                    ].startTime
                )
                if dayofweek == 0:
                    if stime <= ctime:
                        continue
                    timediff = stime - ctime
                else:
                    timediff = dayofweek * 24 * 60 + (stime - ctime)

                if timediff < mintimeandTryChrIt:
                    mintimeandTryChrIt = timediff
                    nearestclasspos = classposition

        return nearestclasspos

    def handleButtonCallback(self, cp: TimetableClassPosition, btnindex: int):
        print("Query details of btnindex: ", btnindex)
        if self.lastButton != -1:
            self.cpbtnlists[self.lastButton].config(relief=tk.RAISED, borderwidth=2)
        self.cpbtnlists[btnindex].config(relief=tk.SOLID, borderwidth=5)
        self.lastButton = btnindex
        cid: TimetableClassIdentity = self.timetable.classids[cp.id]
        self.labelvclassname.config(text=cid.name)
        self.labelvteachername.config(text=cid.teacher)
        self.labelvroomname.config(text=cid.location)
        self.labelvweekstart.config(text=cid.weekTime.startWeek)
        self.labelvweekend.config(text=cid.weekTime.endWeek)

    def popupCreateNewTimetable(self):
        r = messagebox.showwarning(
            "当前课表为空", "当前课表为空，点击【是】前往新建课表向导。"
        )
        if r:
            self.jumpToImporterWindow()

    def jumpToImporterWindow(self):
        TimetableImporterSelectorRenderer(self.timetable)

    def showImporterWindow(self):
        self.mwin.destroy()
        TimetableImporterSelectorRenderer(self.timetable)


class TimetableImporterSelectorRenderer:
    def __init__(self, timeTable: Timetable):
        self.timetable = timeTable
        self.miswin = tk.Tk()
        self.miswin.title("Timetable Importer")
        self.miswin.geometry("300x300")
        txttitle = tk.Label(self.miswin, text="请选择导入方式")
        txttitle.pack(padx=10)
        framebtn = tk.Frame(self.miswin)
        framebtn.pack(pady=10)
        btnweb = tk.Button(
            self.miswin, text="从WakeUp分享口令导入", command=self.showWakeupImporter
        )
        btnweb.pack(pady=10)
        btnjson = tk.Button(
            self.miswin, text="从JSON导入", command=self.showJSONImporter
        )
        btnjson.pack(pady=10)
        btneditor = tk.Button(self.miswin, text="手动编辑", command=self.showEditor)
        btneditor.pack(pady=10)
        self.miswin.mainloop()

    def showWakeupImporter(self):
        self.miswin.destroy()
        TimetableWakeupImporterRenderer(self.timetable)

    def showJSONImporter(self):
        self.miswin.destroy()
        TimetableJSONImporterRenderer(self.timetable)

    def showEditor(self):
        self.miswin.destroy()
        TimetableEditorRenderer(self.timetable)


class TimetableWakeupImporterRenderer:
    def __init__(self, timeTable: Timetable):
        self.timetable = timeTable
        self.timetable.istemplated = False
        self.mwiwin = tk.Tk()
        self.mwiwin.title("导入课表：从WakeUp导入")
        txttitle = tk.Label(self.mwiwin, text="请输入WakeUp分享口令")
        txttitle.pack(padx=10)
        self.entry = tk.Entry(self.mwiwin)
        self.entry.pack(pady=10)
        btn = tk.Button(self.mwiwin, text="导入", command=self.importTimetable)
        btn.pack(pady=10)
        labelnotice = tk.Label(
            self.mwiwin,
            text="""请注意：导入课表后，原有课表将被覆盖！
WakeUp课表导入功能需要网络连接。
分享口令有效期仅30分钟，请及时导入。
受限于Tkinter的颜色显示功能，课程颜色将随机生成而不遵循导入的设置。
WakeUp课程表和本结课作业无关。""",
        )
        labelnotice.pack(pady=30)
        self.mwiwin.mainloop()

    def getSharedToken(self) -> Optional[str]:
        l = self.entry.get()
        if l.startswith(
            "这是来自「WakeUp课程表」的课表分享，30分钟内有效哦，如果失效请朋友再分享一遍叭。为了保护隐私我们选择不监听你的剪贴板，请复制这条消息后，打开App的主界面，右上角第二个按钮 -> 从分享口令导入，按操作提示即可完成导入~分享口令为"
        ):
            pattern = (
                r"这是来自「WakeUp课程表」的课表分享.*分享口令为「([a-zA-Z0-9-_]+)」"
            )
            match = re.search(pattern, l)
            if match:
                return match.group(1)
            else:
                return None
        else:
            if re.search(r"[a-zA-Z0-9-_]+", l):
                return l
            else:
                return None

    def importTimetable(self):
        importer = TimetableWakeupRemoteImporter()
        token = self.getSharedToken()
        print("WakeupSharedToken: ", token)
        if token is None:
            messagebox.showerror("错误", "口令格式错误")
            return
        self.timetable = importer.getTimetable(token)
        if self.timetable is None:
            messagebox.showerror("错误", "口令无效或课表为空")
            return
        self.timetable.saveToJSON()
        messagebox.showinfo("导入成功", "课表已导入成功")
        self.mwiwin.destroy()
        TimetableMainRenderer(self.timetable)


class TimetableJSONImporterRenderer:
    def __init__(self, timeTable: Timetable):
        self.timeTable = timeTable
        self.timeTable.istemplated = False
        messagebox.showwarning(
            "警告",
            "通常情况下，请不要使用JSON导入功能。默认的课程表数据文件存储在timetable.json内。",
        )
        self.mjwin = tk.Tk()
        self.mjwin.title("导入课表：从JSON导入")
        txttitle = tk.Label(self.mjwin, text="请输入JSON文件路径")
        txttitle.pack(padx=10)
        btn = tk.Button(self.mjwin, text="选择文件导入", command=self.importTimetable)
        btn.pack(pady=10)
        self.mjwin.mainloop()

    def importTimetable(self):
        ffp = filedialog.askopenfilename(
            title="选择课表文件", filetypes=[("JSON文件", "*.json")]
        )
        if ffp:
            importer = TimetableJSONImporter()
            self.timeTable = importer.getTimetable(ffp)
            self.timeTable.saveToJSON()
            messagebox.showinfo("导入成功", "课表已导入成功")
            self.mjwin.destroy()
            TimetableMainRenderer(self.timeTable)
        else:
            messagebox.showerror("错误", "未选择文件")


class TimetableEditorRenderer:
    SELECTING = "√"
    NOT_SELECTING = ""

    def __init__(self, timeTable: Timetable):
        self.timetable = timeTable
        self.timetable.istemplated = False
        self.mewin = tk.Tk()
        self.mewin.title("课表手动编辑器")
        self.mewin.geometry("1210x900")

        self.currentColor = self.generateRandomColor()
        self.selectingList: List[List[int]] = []
        self.useExistedId: Optional[TimetableClassIdentity] = None
        self.singleSelectingValue: Optional[List[int]] = None
        self.savedids: List[List[Optional[int]]] = [
            [None for _ in range(11)] for _ in range(7)
        ]
        self.tv = [
            [
                tk.StringVar(self.mewin, value=TimetableEditorRenderer.NOT_SELECTING)
                for _ in range(11)
            ]
            for _ in range(7)
        ]

        framebtnlist = tk.Frame(self.mewin)
        self.btnlist = [
            [
                tk.Button(
                    framebtnlist,
                    textvariable=self.tv[i][j],
                    command=lambda i=i, j=j: self.handleButtonCallback(i, j),
                    height=2,
                    width=6,
                    cursor="hand2",
                    wraplength=70,
                    justify=tk.CENTER,
                )
                for j in range(11)
            ]
            for i in range(7)
        ]

        labelweeks = [
            tk.Label(framebtnlist, text=weekname)
            for weekname in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        ]
        labelclasstimes = [
            tk.Label(framebtnlist, text=classtimes)
            for classtimes in [
                f"{time.startTime}-{time.endTime}"
                for time in self.timetable.columnTimes
            ]
        ]
        for index, labelweek in enumerate(labelweeks):
            labelweek.grid(row=0, column=index + 1)
        for index, labelclasstime in enumerate(labelclasstimes):
            labelclasstime.grid(row=index + 1, column=0, padx=5)

        for i in range(7):
            for j in range(11):
                self.btnlist[i][j].grid(row=j + 1, column=i + 1, padx=5, pady=5)

        # *** w1 w2 w3 w4 w5 w6 w7
        # t01
        # t02
        # t03
        # t04
        # t05
        # t06
        # t07
        # t08
        # t09
        # t10
        # t11
        # framebtnlist 通过 grid(row, column) 进行渲染。

        framebtnlist.grid(row=0, column=0, padx=10, pady=10)

        frameright = tk.Frame(self.mewin)
        frameright.grid(row=0, column=1, padx=10, pady=10)

        lbfdetails = tk.LabelFrame(frameright, text="课表详情")
        frametimetablename = tk.Frame(lbfdetails)
        labeltimetablename = tk.Label(frametimetablename, text="课表名称：")
        labeltimetablename.grid(row=0, column=0, padx=3, pady=3)
        entrytimetablename = tk.Entry(frametimetablename)
        entrytimetablename.insert(0, self.timetable.name)
        entrytimetablename.grid(row=0, column=1, padx=3, pady=3)
        frametimetablename.pack(padx=20, pady=4, anchor="w")

        frametimetablectime = tk.Frame(lbfdetails)
        labeltimetablectime = tk.Label(frametimetablectime, text="上课时间：")
        labeltimetablectime.grid(row=0, column=0, padx=3, pady=3)
        btntimetablectime = tk.Button(frametimetablectime, text="编辑")
        btntimetablectime.config(state=tk.DISABLED)
        btntimetablectime.grid(row=0, column=1, padx=3, pady=3)
        frametimetablectime.pack(padx=20, pady=4, anchor="w")

        labeldonotedited = tk.Label(
            lbfdetails, text="当前已导入河北大学的正确上课课程时间\n无需进行更改。"
        )
        labeldonotedited.pack(pady=3)
        lbfdetails.grid(row=0, column=0, padx=3, pady=10, sticky="ew")

        lbfclassinfo = tk.LabelFrame(frameright, text="新建课程")
        lbfclassinfo.grid(row=1, column=0, padx=10, pady=10)

        self.tvclassname = tk.StringVar(self.mewin, value="")
        self.tvteachername = tk.StringVar(self.mewin, value="")
        self.tvroomname = tk.StringVar(self.mewin, value="")
        self.tvweekstart = tk.StringVar(self.mewin, value="")
        self.tvweekend = tk.StringVar(self.mewin, value="")
        self.tvclassname.trace_add("write", self.classnameChanged)

        frameclassname = tk.Frame(lbfclassinfo)
        labelclassname = tk.Label(frameclassname, text="课程名称：")
        labelclassname.grid(row=0, column=0, padx=3, pady=3)
        entryclassname = tk.Entry(frameclassname, textvariable=self.tvclassname)
        entryclassname.grid(row=0, column=1, padx=3, pady=3)
        frameclassname.pack(padx=20, pady=4, anchor="w")

        frameteachername = tk.Frame(lbfclassinfo)
        labelteachername = tk.Label(frameteachername, text="教师姓名：")
        labelteachername.grid(row=0, column=0, padx=3, pady=3)
        entryteachername = tk.Entry(frameteachername, textvariable=self.tvteachername)
        entryteachername.grid(row=0, column=1, padx=3, pady=3)
        frameteachername.pack(padx=20, pady=4, anchor="w")

        frameroomname = tk.Frame(lbfclassinfo)
        labelroomname = tk.Label(frameroomname, text="教室名称：")
        labelroomname.grid(row=0, column=0, padx=3, pady=3)
        entryroomname = tk.Entry(frameroomname, textvariable=self.tvroomname)
        entryroomname.grid(row=0, column=1, padx=3, pady=3)
        frameroomname.pack(padx=20, pady=4, anchor="w")

        frameweekstart = tk.Frame(lbfclassinfo)
        labelweekstart = tk.Label(frameweekstart, text="起始周：")
        labelweekstart.grid(row=0, column=0, padx=3, pady=3)
        entryweekstart = tk.Entry(frameweekstart, textvariable=self.tvweekstart)
        entryweekstart.grid(row=0, column=1, padx=3, pady=3)
        frameweekstart.pack(padx=20, pady=4, anchor="w")

        frameweekend = tk.Frame(lbfclassinfo)
        labelweekend = tk.Label(frameweekend, text="结束周：")
        labelweekend.grid(row=0, column=0, padx=3, pady=3)
        entryweekend = tk.Entry(frameweekend, textvariable=self.tvweekend)
        entryweekend.grid(row=0, column=1, padx=3, pady=3)
        frameweekend.pack(padx=20, pady=4, anchor="w")

        framecolorchooser = tk.Frame(lbfclassinfo)
        btncolorchooser = tk.Button(
            framecolorchooser, text="选择颜色", command=self.chooseColor, cursor="hand2"
        )
        btncolorchooser.grid(row=0, column=0, padx=3, pady=3)
        labelcolorchooser = tk.Label(framecolorchooser, text="点击随机设置颜色：")
        labelcolorchooser.grid(row=0, column=1, padx=3, pady=3)
        self.labelcolordisplay = tk.Button(
            framecolorchooser,
            bg=self.currentColor,
            command=self.regenerateRandomColor,
            width=3,
            height=1,
            cursor="hand2",
        )
        self.labelcolordisplay.grid(row=0, column=2, padx=3, pady=3)
        framecolorchooser.pack(padx=20, pady=4, anchor="w")

        framecid = tk.Frame(lbfclassinfo)
        labelcid = tk.Label(framecid, text="使用已有课程：")
        labelcid.grid(row=0, column=0, padx=3, pady=3)
        self.combocid = ttk.Combobox(
            framecid, values=[cid.name for cid in self.timetable.classids]
        )
        self.combocid.bind("<<ComboboxSelected>>", self.useExistedClass)
        self.combocid.grid(row=0, column=1, padx=3, pady=3)
        framecid.pack(padx=20, pady=4, anchor="w")
        self.labelisclassexisted = tk.Label(framecid, text="这是一个新课程！")
        self.labelisclassexisted.grid(row=1, column=0, columnspan=2, padx=3, pady=3)

        framecidbtn = tk.Frame(lbfclassinfo)
        self.btnuseexisted = tk.Button(
            framecidbtn,
            text="不使用已有课程",
            command=self.useExistedClass,
            state=tk.DISABLED,
        )
        self.btnuseexisted.grid(row=0, column=0, padx=3, pady=3)
        self.btndelete = tk.Button(
            framecidbtn, text="删除课程", command=self.deleteClass, state=tk.DISABLED
        )
        self.btndelete.grid(row=0, column=1, padx=3, pady=3)
        self.btnadd = tk.Button(
            framecidbtn, text="添加课程", command=self.saveToTimetable, cursor="hand2"
        )
        self.btnadd.grid(row=0, column=2, padx=3, pady=3)
        framecidbtn.pack(pady=3)

        self.btnexit = tk.Button(
            frameright, text="退出", command=self.backToMainWindow, cursor="hand2"
        )
        self.btnexit.grid(row=2, column=0, padx=10, pady=10)
        self.renderCurrentTimetable()
        self.mewin.mainloop()

    def renderCurrentTimetable(self):
        for index, ct in enumerate(self.timetable.classes):
            for c in ct:
                if c == []:
                    continue
                cid = self.timetable.classids[c.id]
                for i in range(c.time.startTime - 1, c.time.endTime):
                    self.tv[index][i].set(cid.name)
                    self.btnlist[index][i].config(bg=cid.color)
                    self.savedids[index][i] = c.id

    def backToMainWindow(self):
        self.mewin.destroy()
        self.timetable.saveToJSON()
        TimetableMainRenderer(self.timetable)

    def selectExistedClassid(self):
        self.useExistedId = self.timetable.classids[
            [cid.name for cid in self.timetable.classids].index(self.combocid.get())
        ]

    def updateComboClassidsValues(self):
        self.combocid.config(values=[cid.name for cid in self.timetable.classids])

    def deleteClass(self):
        self.btndelete.config(state=tk.DISABLED)
        self.btndelete.config(cursor="arrow")
        classes_to_remove: List[TimetableClassPosition] = []
        for class_item in self.timetable.classes[self.singleSelectingValue[0]]:
            if class_item == []:
                continue
            start_node = class_item.time.startTime
            steps = class_item.time.endTime - start_node + 1
            if start_node <= self.singleSelectingValue[1] < start_node + steps:
                classes_to_remove.append(class_item)
                for j in range(start_node, start_node + steps):
                    self.tv[self.singleSelectingValue[0]][j].set(
                        TimetableEditorRenderer.NOT_SELECTING
                    )
                    self.btnlist[self.singleSelectingValue[0]][j].config(
                        bg="SystemButtonFace"
                    )

        for item in classes_to_remove:
            self.timetable.classes[self.singleSelectingValue[0]].remove(item)

    def setCurrentClassidToValue(self):
        if self.singleSelectingValue is None:
            return
        self.selectExistedClassid()
        cid = self.useExistedId
        self.tvclassname.set(cid.name)
        self.tvteachername.set(cid.teacher)
        self.tvroomname.set(cid.location)
        self.tvweekstart.set(cid.weekTime.startWeek)
        self.tvweekend.set(cid.weekTime.endWeek)

    def showCurrentClassid(self, i: int, j: int):
        if self.savedids[i][j] is None:
            return
        cid: TimetableClassIdentity = self.timetable.classids[self.savedids[i][j]]
        self.tvclassname.set(cid.name)
        self.tvteachername.set(cid.teacher)
        self.tvroomname.set(cid.location)
        self.tvweekstart.set(cid.weekTime.startWeek)
        self.tvweekend.set(cid.weekTime.endWeek)
        self.btndelete.config(state=tk.NORMAL)
        self.btndelete.config(cursor="hand2")

    def saveToTimetable(self):
        ws = self.tvweekstart.get()
        we = self.tvweekend.get()
        if not ws.isdigit() or not we.isdigit():
            messagebox.showerror("错误", "周数必须为数字！")
            return
        if int(ws) > int(we):
            messagebox.showerror("错误", "起始周必须小于等于结束周！")
            return
        if int(ws) <= 0 or int(we) <= 0:
            messagebox.showerror("错误", "周数必须为正整数！")
            return
        if self.tvclassname.get() == "":
            messagebox.showerror("错误", "课程名称不能为空！")
            return
        if not self.selectingList:
            messagebox.showerror("错误", "未选择任何课程时间！")
            return

        if self.useExistedId is None:
            cid = TimetableClassIdentity(
                self.tvclassname.get(),
                self.tvteachername.get(),
                self.tvroomname.get(),
                TimetableClassWeekTime(int(ws), int(we)),
                self.currentColor,
            )
            ciid = self.timetable.addClassId(cid)
        else:
            cid = self.useExistedId
            ciid = self.timetable.classids.index(cid)

        cps = [[] for _ in range(7)]
        osl: List[List[int]] = [[] for _ in range(7)]
        for pos in self.selectingList:
            self.tv[pos[0]][pos[1]].set(self.tvclassname.get())
            self.btnlist[pos[0]][pos[1]].config(bg=self.currentColor)
            self.savedids[pos[0]][pos[1]] = ciid
            osl[pos[0]].append(pos[1])
        for i in range(7):
            osl[i].sort(reverse=True)
            if not osl[i]:
                continue
            start = osl[i][0]
            count = 1

            for j in range(1, len(osl[i])):
                if osl[i][j] == osl[i][j - 1] - 1:
                    count += 1
                else:
                    cps[i].append([start - count + 1, count])
                    start = osl[i][j]
                    count = 1

            cps[i].append([start - count + 1, count])
        print("Editor.saveToTimetable: ", cps)
        for index, weekc in enumerate(cps):
            for c in weekc:
                self.timetable.classes[index].append(
                    TimetableClassPosition(
                        ciid, TimetableClassTime(c[0] + 1, c[0] + c[1])
                    )
                )
        self.selectingList.clear()
        self.combocid.set("")
        self.singleSelectingValue = None
        self.updateComboClassidsValues()
        self.tvclassname.set("")
        self.tvteachername.set("")
        self.tvroomname.set("")
        self.tvweekstart.set("")
        self.tvweekend.set("")
        self.regenerateRandomColor()

    def useNewClass(self):
        self.btnuseexisted.config(text="使用已有课程", command=self.useExistedClass)
        self.classnameChanged()
        self.useExistedId = None

    def useExistedClass(self, *args):
        ccn = self.combocid.get()
        cnl = [cid.name for cid in self.timetable.classids]
        self.btnuseexisted.config(text="不使用现有课程", command=self.useNewClass)
        self.useExistedId = self.timetable.classids[cnl.index(ccn)]
        self.tvclassname.set(self.useExistedId.name)
        self.tvteachername.set(self.useExistedId.teacher)
        self.tvroomname.set(self.useExistedId.location)
        self.tvweekstart.set(
            self.useExistedId.weekTime.startWeek
            if self.useExistedId.weekTime is not None
            else ""
        )
        self.tvweekend.set(
            self.useExistedId.weekTime.endWeek
            if self.useExistedId.weekTime is not None
            else ""
        )
        self.currentColor = self.useExistedId.color
        self.labelcolordisplay.config(bg=self.currentColor)

    def classnameChanged(self, *args):
        ccn = self.tvclassname.get()
        cnl = [cid.name for cid in self.timetable.classids]
        if ccn in cnl:
            self.labelisclassexisted.config(
                text="课程已存在！可以使用已有课程或创建新课程。"
            )
            self.btnuseexisted.config(state=tk.NORMAL)
            self.btnuseexisted.config(cursor="hand2")
        else:
            self.labelisclassexisted.config(text="这是一个新课程！")
            self.btnuseexisted.config(state=tk.DISABLED)
            self.btnuseexisted.config(cursor="arrow")

    def chooseColor(self):
        color = colorchooser.askcolor(title="选择颜色")
        if color[1]:
            self.currentColor = color[1]
            self.labelcolordisplay.config(bg=self.currentColor)

    def regenerateRandomColor(self):
        self.currentColor = self.generateRandomColor()
        self.labelcolordisplay.config(bg=self.currentColor)

    def generateRandomColor(self) -> str:
        r = random.randint(127, 255)
        g = random.randint(127, 255)
        b = random.randint(127, 255)
        return f"#{r:02X}{g:02X}{b:02X}"

    def handleButtonCallback(self, i: int, j: int):
        if self.tv[i][j].get() == TimetableEditorRenderer.NOT_SELECTING:
            self.tv[i][j].set(TimetableEditorRenderer.SELECTING)
            self.selectingList.append([i, j])
        elif self.tv[i][j].get() == TimetableEditorRenderer.SELECTING:
            self.tv[i][j].set(TimetableEditorRenderer.NOT_SELECTING)
            try:
                self.selectingList.remove([i, j])
            except ValueError:
                pass
        else:

            self.singleSelectingValue = [i, j]
            self.showCurrentClassid(i, j)
        print(f"Button {i},{j} clicked")


if __name__ == "__main__":
    # Enabled High DPI awareness for Windows 10/11
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    cTimetable = TimetableJSONImporter.readLocalTimetableJSONIfExisted()
    if cTimetable is None:
        # 如果当前不存在课表，则新建一个课表
        # 调用 cTimetable = Timetable.createBlankTimetable() 生成一个空白课表
        # 调用 cTimetable = Timetable.createHBUTemplatedTimetable() 生成一个以河北大学为模板的课表
        cTimetable = Timetable.createHBUTemplatedTimetable()
    TimetableMainRenderer(cTimetable)

    # 程序首先使用 TimetableMainRenderer 渲染课表主界面
    # 通过判断 timetable.istemplated 来判断是否为空的模板课表
    # 如果是模板课表，渲染 TimetableImporterSelectorRenderer 引导用户选择导入方式
    # TimetableJSONImporterRenderer 从JSON导入课表
    # TimetableWakeupImporterRenderer 从WakeUp分享口令导入课表（依赖于 TimetableJSONImporter）
    # TimetableEditorRenderer 手动编辑课表
