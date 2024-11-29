"""
Author: aquamarine5 && aquamarine5_@outlook.com
Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
"""

import json
import random
from tkinter import filedialog, messagebox
from typing import List, Optional

import urllib.request
import tkinter as tk
import urllib.error

from torch import R

CURRENT_TIMETABLE_JSON_PATH = "timetable.json"


class TimetableClassTime:
    def __init__(self, startTime: int, endTime: int):
        self.startTime = startTime
        self.endTime = endTime


class TimetableClassWeekTime:
    def __init__(self, startWeek: int, endWeek: int):
        self.startWeek = startWeek
        self.endWeek = endWeek


class TimetableColumnTime:
    def __init__(self, startTime: str, endTime: str):
        self.startTime = startTime
        self.endTime = endTime


class TimetableClassPosition:
    def __init__(self, id: int, time: TimetableClassTime):
        self.id = id
        self.time = time


class TimetableSingleClassID:
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
    def __init__(
        self,
        classes: List[List[TimetableClassPosition]],
        classids: List[TimetableSingleClassID],
        columnTimes: List[TimetableColumnTime],
        name: str,
    ):
        self.classes = classes
        self.columnTimes = columnTimes
        self.name = name
        self.classids = classids

    def saveToJSON(filepath: str = CURRENT_TIMETABLE_JSON_PATH):
        c = []

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

    def getTimetable(self, file: str = CURRENT_TIMETABLE_JSON_PATH):
        with open(file, "r") as f:
            c = f.read()
            wri = TimetableWakeupRemoteImporter()
            return wri.parseByJSON(c)


class TimetableWakeupRemoteImporter(TimetableImporterInterface):
    def __init__(self):
        pass

    def getTimetable(self, shareId: str) -> Timetable:
        req = urllib.request.Request(
            f"https://i.wakeup.fun/share_schedule/get?key={shareId}"
        )
        req.add_header("version", "250")
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read()
                data_str = data.decode("utf-8")
                json_data = json.loads(data_str)
        except urllib.error.HTTPError as e:
            raise e
        return self.parseByJSON(json_data["data"])

    def parseByJSON(self, timetable_json: str) -> Timetable:
        if timetable_json == "":
            raise ValueError("No timetable found")
        else:
            self.timetable_data = timetable_json["data"].split("\n")
            self.timetable_time = json.loads(self.timetable_data[1])
            self.timetable_details = json.loads(self.timetable_data[2])
            self.timetable_classid = json.loads(self.timetable_data[3])
            self.timetable_classtime = json.loads(self.timetable_data[4])
            self._parseBaseInformation()
            return self._parseTimetable()

    def _parseBaseInformation(self):
        self.timetable_name: str = self.timetable_details.tableName
        classtimes: List[TimetableColumnTime] = []
        for ctp in self.timetable_classtime[: int(self.timetable_details.nodes)]:
            classtimes.append(TimetableColumnTime(ctp.startTime, ctp.endTime))
        self.timetable_columntimes = classtimes

    def _parseTimetable(self) -> Timetable:
        ttl: List[List[TimetableClassPosition]] = [[] for _ in range(7)]
        tpl: List[TimetableSingleClassID] = []
        for clsid in self.timetable_classid:
            tpl.append(
                TimetableSingleClassID(clsid.courseName, None, None, None, clsid.color)
            )
        for cls in self.timetable_classtime:
            ttl[cls.day - 1].append(
                TimetableClassPosition(
                    cls.id,
                    TimetableClassTime(cls.startNode, cls.startNode + cls.step - 1),
                )
            )
            tpl[cls.id].teacher = cls.teacher
            tpl[cls.id].location = cls.room
            tpl[cls.id].weekTime = TimetableClassWeekTime(cls.startWeek, cls.endWeek)
        return Timetable(ttl, tpl, self.timetable_columntimes, self.timetable_name)


class TimetableMainRenderer:
    def __init__(self):
        # Enabled High DPI awareness for Windows 10/11
        try:
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.mwin = tk.Tk("Timetable Displayer")
        btnimporter = tk.Button(
            self.mwin, text="新建课表", command=self.showImporterWindow
        )
        btnimporter.pack(pady=10)
        self.mwin.mainloop()

    def showImporterWindow(self):
        TimetableImporterSelectorRenderer()


class TimetableImporterSelectorRenderer:
    def __init__(self):
        self.miswin = tk.Tk("Timetable Importer")
        self.miswin.geometry("300x300")
        txttitle = tk.Label(self.miswin, text="请选择导入方式")
        txttitle.pack(padx=10)
        framebtn = tk.Frame(self.miswin)
        framebtn.pack(pady=10)
        btnweb = tk.Button(
            self.miswin, text="从WakeUp导入", command=self.showWakeupImporter
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
        TimetableWakeupImporterRenderer()

    def showJSONImporter(self):
        self.miswin.destroy()
        TimetableJSONImporterRenderer()

    def showEditor(self):
        self.miswin.destroy()
        TimetableEditorRenderer()


class TimetableWakeupImporterRenderer:
    def __init__(self):
        self.mwiwin = tk.Tk("WakeUp导入")
        txttitle = tk.Label(self.mwiwin, text="请输入WakeUp分享链接")
        txttitle.pack(padx=10)
        self.entry = tk.Entry(self.mwiwin)
        self.entry.pack(pady=10)
        btn = tk.Button(self.mwiwin, text="导入", command=self.importTimetable)
        btn.pack(pady=10)
        self.mwiwin.mainloop()

    def importTimetable(self):
        importer = TimetableWakeupRemoteImporter()
        importer.getTimetable(self.entry.get()).saveToJSON()
        messagebox.showinfo("导入成功", "课表已导入成功")
        self.mwiwin.destroy()
        TimetableMainRenderer()


class TimetableJSONImporterRenderer:
    def __init__(self):
        self.mjwin = tk.Tk("JSON导入")
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
            importer.getTimetable(ffp).saveToJSON()
            messagebox.showinfo("导入成功", "课表已导入成功")
            self.mjwin.destroy()
            TimetableMainRenderer()
        else:
            messagebox.showerror("错误", "未选择文件")


class TimetableEditorRenderer:
    SELECTING = "√"
    NOT_SELECTING = ""

    def __init__(self):
        self.mewin = tk.Tk("手动编辑")
        self.mewin.geometry("600x600")
        self.selectingList = []
        framebtnlist = tk.Frame(self.mewin)
        self.tv = [
            [
                tk.StringVar(self.mewin, value=TimetableEditorRenderer.NOT_SELECTING)
                for _ in range(11)
            ]
            for _ in range(7)
        ]
        self.btnlist = [
            [
                tk.Button(
                    framebtnlist,
                    textvariable=self.tv[i][j],
                    command=lambda i=i, j=j: self.handleButtonCallback(i, j),
                    height=10,
                    width=10,
                )
            ]
            for i in range(7)
            for j in range(11)
        ]
        for i in range(7):
            for j in range(11):
                self.btnlist[i][j].grid(row=i, column=j, padx=5, pady=5)

        entryclassname = tk.Entry(self.mewin)
        entryclassname.pack(pady=10)
        entryteachername = tk.Entry(self.mewin)
        entryteachername.pack(pady=10)
        entryroomname = tk.Entry(self.mewin)
        entryroomname.pack(pady=10)
        entryweekstart = tk.Entry(self.mewin)
        entryweekstart.pack(pady=10)
        entryweekend = tk.Entry(self.mewin)
        entryweekend.pack(pady=10)
        btncolorchooser = tk.Button(
            self.mewin, text="选择颜色", command=self.chooseColor
        )
        self.mewin.mainloop()

    def chooseColor(self):
        pass

    def generateRandomColor(self) -> str:
        r = random.randint(127, 255)
        g = random.randint(127, 255)
        b = random.randint(127, 255)
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

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
        print(f"Button {i},{j} clicked")

    def saveClass(self):
        for pos in self.selectingList:
            self.tv[pos[0]][pos[1]].set(TimetableEditorRenderer.NOT_SELECTING)


if __name__ == "__main__":
    TimetableMainRenderer()
