import tkinter as tk
import math


class Question1:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Question 1")
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="white")
        self.canvas.pack()
        self.x_scale = 80
        self.y_scale = 35
        self.origin_x = 200
        self.origin_y = 200
        self.draw_axes()
        self.draw_radiation()
        self.root.mainloop()

    def draw_axes(self):
        self.canvas.create_line(
            0, self.origin_y, 400, self.origin_y, fill="red", width=1
        )
        self.canvas.create_line(
            self.origin_x, 0, self.origin_x, 400, fill="red", width=1
        )

    def formula_calculate(self, x):
        return -3 * x**3 - 3 * x**2 + 4 * math.sin(x)

    def get_quadrant_color(self, x, y):
        if x >= 0 and y >= 0:
            return "black"
        elif x < 0 and y >= 0:
            return "red"
        elif x < 0 and y < 0:
            return "green"
        else:
            return "blue"

    def draw_radiation(self):
        x = -1.7
        while x <= 1.7:
            y = self.formula_calculate(x)
            canvas_x = self.origin_x + x * self.x_scale
            canvas_y = self.origin_y - y * self.y_scale
            color = self.get_quadrant_color(x, y)
            self.canvas.create_line(
                self.origin_x, self.origin_y, canvas_x, canvas_y, fill=color, width=1
            )

            x += 0.02


class Question2:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Question2")
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="white")
        self.canvas.pack()
        self.x_scale = 80
        self.y_scale = 35
        self.origin_x = 200
        self.origin_y = 200
        self.draw_axes()
        self.draw_ribbon()
        self.root.mainloop()

    def draw_axes(self):
        self.canvas.create_line(
            0, self.origin_y, 400, self.origin_y, fill="red", width=1
        )
        self.canvas.create_line(
            self.origin_x, 0, self.origin_x, 400, fill="red", width=1
        )

    def calculate_y(self, x):
        return -3 * x**3 - 3 * x**2 + 4 * math.sin(x)

    def is_rising(self, x):
        h = 0.01
        y1 = self.calculate_y(x)
        y2 = self.calculate_y(x + h)
        return (y2 - y1) / h > 0

    def draw_ribbon(self):
        x = -1.7
        while x <= 1.7:
            y = self.calculate_y(x)
            canvas_x1 = self.origin_x + x * self.x_scale
            canvas_y1 = self.origin_y - y * self.y_scale
            offset_x = x + 20 / self.x_scale
            offset_y = y + 20 / self.y_scale
            canvas_x2 = self.origin_x + offset_x * self.x_scale
            canvas_y2 = self.origin_y - offset_y * self.y_scale
            color = "red" if self.is_rising(x) else "blue"
            self.canvas.create_line(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill=color, width=1
            )
            x += 0.01


class Question3:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Question 3")
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.canvas.pack()
        self.wh = 300
        self.hh = 300
        self.draw_axes()
        self.draw_flower_bud()
        self.root.mainloop()

    def draw_axes(self):
        self.canvas.create_line(0, self.hh, 600, self.hh, fill="red", width=1)
        self.canvas.create_line(self.wh, 0, self.wh, 600, fill="red", width=1)

    def calculate_point(self, t):
        x = (self.wh / 4) * (-2 * math.sin(2 * t) + math.sin(t))
        y = (self.hh / 4) * (-2 * math.cos(2 * t) + math.cos(t))
        return x, y

    def get_color(self, x, y):
        return "red" if y < 0 else "green"

    def draw_flower_bud(self):
        t = 0
        while t <= 2 * math.pi:
            x, y = self.calculate_point(t)
            canvas_x = self.wh + x
            canvas_y1 = self.hh - (y - 10)
            canvas_y2 = self.hh - (y + 10)
            color = self.get_color(x, y)
            self.canvas.create_line(
                canvas_x, canvas_y1, canvas_x, canvas_y2, fill=color, width=1
            )
            t += 0.01


if __name__ == "__main__":
    Question1()
    Question2()
    Question3()
