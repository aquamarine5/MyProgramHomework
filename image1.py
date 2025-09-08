import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 设置中文字体支持
plt.rcParams["font.sans-serif"] = [
    "SimHei",
    "Microsoft YaHei",
]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

# 问题三 (各点效率)
plt.rcParams["font.family"] = "SimHei"


def roundn(x, n):
    """MATLAB roundn函数的Python实现"""
    return np.round(x, -n)


def rectint(rect1, rect2):
    """计算两个矩形的重叠面积 - MATLAB rectint函数的Python实现"""
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # 计算重叠区域的边界
    left = max(x1, x2)
    right = min(x1 + w1, x2 + w2)
    top = max(y1, y2)
    bottom = min(y1 + h1, y2 + h2)

    # 如果没有重叠，返回0
    if left >= right or top >= bottom:
        return 0

    # 返回重叠面积
    return (right - left) * (bottom - top)


def SUN(month, day):
    """太阳位置计算函数 - 需要根据实际需求实现"""
    # 这里是示例实现，需要根据实际的太阳位置计算公式来实现
    A = 0.5  # 太阳方位角示例值
    B = 0.8  # 太阳高度角示例值
    return A, B


def f1(xyz, l, w, N, A, B, x0, y0):
    """遮挡效率"""
    z0 = 84
    a = np.array(
        [
            np.sin(np.radians(B)) * np.cos(np.radians(A)),
            np.cos(np.radians(B)) * np.cos(np.radians(A)),
            np.sin(np.radians(A)),
        ]
    )  # 入射光

    tt = np.zeros((len(xyz), 5))

    for i in range(len(xyz)):
        m = np.sqrt(
            xyz[i, 0] ** 2 + xyz[i, 1] ** 2 + xyz[i, 2] ** 2
        )  # 修正：第二项应该是y坐标
        # h = np.sqrt((xyz[i,0]-x0)**2 + (xyz[i,1]-y0)**2 + (xyz[i,2]-z0)**2)

        r_vec = np.array([-xyz[i, 0] + x0, -xyz[i, 1] + y0, -xyz[i, 2] + z0])
        r_norm = np.sqrt(
            (xyz[i, 0] - x0) ** 2 + (xyz[i, 1] - y0) ** 2 + (xyz[i, 2] - z0) ** 2
        )
        r = r_vec / r_norm  # 反射向量

        n = (r - a) / np.linalg.norm(r - a)  # 法向量
        n = np.real(n)

        # 镜面高度角、方位角
        An = np.degrees(np.arccos(n[2]))
        Bn = np.degrees(np.arctan(n[0] / n[1]))

        # 翻转矩阵
        ss = np.array(
            [
                [
                    np.cos(np.radians(Bn)),
                    np.sin(np.radians(Bn)) * np.sin(np.radians(An)),
                    -np.sin(np.radians(Bn)) * np.cos(np.radians(An)),
                ],
                [
                    -np.sin(np.radians(Bn)),
                    np.cos(np.radians(Bn)) * np.sin(np.radians(An)),
                    -np.cos(np.radians(Bn)) * np.cos(np.radians(An)),
                ],
                [0, np.cos(np.radians(An)), np.sin(np.radians(An))],
            ]
        )

        v1 = (ss @ np.array([-0.5 * l, -0.5 * w, 0])).T + xyz[i, :]  # 左下角
        v2 = (ss @ np.array([0.5 * l, -0.5 * w, 0])).T + xyz[i, :]
        v3 = (ss @ np.array([-0.5 * l, 0.5 * w, 0])).T + xyz[i, :]

        tt[i, 0] = v1[0]
        tt[i, 1] = v1[1]
        tt[i, 3] = np.real(np.abs(np.sum((v1 - v2) * a)))
        tt[i, 2] = np.real(np.abs(np.sum((v1 - v3) * a)))

    num = tt.shape[0]
    # 计算重叠面积
    for i in range(num):
        areas = 0
        for j in range(i + 1, num):
            area = rectint(tt[i, :4], tt[j, :4])  # 两块之间的重叠
            areas = areas + area  # 累加
        tt[i, 4] = areas

    SSS = (88 / np.tan(np.radians(A)) - 100) * 7
    if SSS < 0:
        SSS = 0

    e1 = 1 - (np.sum(tt[:, 4]) + SSS) / N / l / w
    return e1


def f2(xyz, N, x0, y0, A, B):
    """余弦效率"""
    z0 = 84
    SS = np.zeros(len(xyz))

    for i in range(N):
        b = np.array([xyz[i, 0] - x0, xyz[i, 1] - y0, xyz[i, 2] - z0])  # 反射光线
        b = -1 * b
        a = np.array(
            [
                np.sin(np.radians(B)) * np.cos(np.radians(A)),
                np.cos(np.radians(B)) * np.cos(np.radians(A)),
                np.sin(np.radians(A)),
            ]
        )  # 入射光线

        ta = np.degrees(
            np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        )  # 入射光线与反射光线夹角
        SS[i] = np.real(np.cos(np.radians(ta / 2)))

    e2 = np.mean(SS)
    return e2, SS


def f3(xyz, N, x0, y0):
    """大气透射率"""
    z0 = 84
    SS = np.zeros(len(xyz))

    for i in range(N):
        dHR = np.sqrt(
            (xyz[i, 0] - x0) ** 2 + (xyz[i, 1] - y0) ** 2 + (xyz[i, 2] - z0) ** 2
        )
        SS[i] = 0.99321 - 0.0001176 * dHR + 1.97e-8 * dHR**2

    e3 = np.mean(SS)
    return e3, SS


def f4(xyz, l, w, N, A, B, x0, y0):
    """截断效率"""
    z0 = 84
    a = np.array(
        [
            np.sin(np.radians(B)) * np.cos(np.radians(A)),
            np.cos(np.radians(B)) * np.cos(np.radians(A)),
            np.sin(np.radians(A)),
        ]
    )  # 入射光线

    SS = np.zeros(N)

    for i in range(N):
        sum1 = 0
        sum2 = 0
        m = np.sqrt(
            xyz[i, 0] ** 2 + xyz[i, 1] ** 2 + xyz[i, 2] ** 2
        )  # 修正：第二项应该是y坐标
        # h = np.sqrt((xyz[i,0]-x0)**2 + (xyz[i,1]-y0)**2 + (xyz[i,2]-z0)**2)

        r_vec = np.array([-xyz[i, 0] + x0, -xyz[i, 1] + y0, -xyz[i, 2] + z0])
        r_norm = np.sqrt(
            (xyz[i, 0] - x0) ** 2 + (xyz[i, 1] - y0) ** 2 + (xyz[i, 2] - z0) ** 2
        )
        r = r_vec / r_norm  # 反射向量

        n = (r - a) / np.linalg.norm(r - a)  # 法向量
        n = np.real(n)

        # 镜面高度角、方位角
        An = np.degrees(np.arccos(n[2]))
        Bn = np.degrees(np.arctan(n[0] / n[1]))

        # 翻转矩阵
        ss = np.array(
            [
                [
                    np.cos(np.radians(Bn)),
                    np.sin(np.radians(Bn)) * np.sin(np.radians(An)),
                    -np.sin(np.radians(Bn)) * np.cos(np.radians(An)),
                ],
                [
                    -np.sin(np.radians(Bn)),
                    np.cos(np.radians(Bn)) * np.sin(np.radians(An)),
                    -np.cos(np.radians(Bn)) * np.cos(np.radians(An)),
                ],
                [0, np.cos(np.radians(An)), np.sin(np.radians(An))],
            ]
        )

        sss = np.array(
            [
                [
                    np.cos(np.radians(B)),
                    np.sin(np.radians(B)) * np.sin(np.radians(A)),
                    np.sin(np.radians(B)) * np.cos(np.radians(A)),
                ],
                [
                    -np.sin(np.radians(B)),
                    np.cos(np.radians(B)) * np.sin(np.radians(A)),
                    np.cos(np.radians(B)) * np.cos(np.radians(A)),
                ],
                [0, np.cos(np.radians(A)), np.sin(np.radians(A))],
            ]
        )

        for j in range(10000):  # 模拟次数
            AA = (
                sss
                @ np.array(
                    [
                        np.random.rand() * 4.64998e3,
                        np.random.rand() * 2.16223e-5,
                        1 - np.random.rand() * 2e-4,
                    ]
                )
            ).T

            R = 2 * np.dot(AA, n) * n - AA
            p = (
                ss
                @ np.array(
                    [-l * 0.5 * np.random.rand(), -w * 0.5 * np.random.rand(), 0]
                )
            ).T + xyz[
                i, :
            ]  # 随机一点

            # 定义直线的参数方程
            cross_prod = np.cross(np.array([p[0] - x0, p[1] - y0, p[2] - z0]), R)
            d = np.linalg.norm(cross_prod) / np.sqrt(R[0] ** 2 + R[1] ** 2 + R[2] ** 2)

            if d < 4:
                # 直线与圆柱曲面不相交
                sum1 = sum1 + 1
            else:
                sum2 = sum2 + 1

        SS[i] = sum1 / 100

    e4 = np.sum(SS) / N
    return e4, SS


# 主程序
r = 100
n = 88  # 分割数量
u = np.array([[0, 0]])
xx = n

for i in range(1, 101):
    if r > n * 13 / 2 / np.pi:
        r = r + 13
        # r = r + (i-1) * 20 / 7 * np.pi * 70 / n
        if i % 2 == 0:
            angle = np.arange(np.pi, 3 * np.pi, 13 / r)
        else:
            angle = np.arange(0, 2 * np.pi, 13 / r)
    else:
        r = r + 2 * np.pi * r / n
        if i % 2 == 0:
            angle = np.arange(np.pi, 3 * np.pi, 2 * np.pi / n)
        else:
            angle = np.arange(0, 2 * np.pi, 2 * np.pi / n)

    x = r * np.cos(angle)
    y = r * np.sin(angle)
    new_points = np.column_stack((x, y))
    u = np.vstack((u, new_points))

xyz = u[1:, :]  # 去除第一行
N = xyz.shape[0]
UO = 2000

# 修复数组长度问题
if N >= UO:
    HHH = np.linspace(2, 6, UO)
    HHHH = np.concatenate([HHH, np.full(N - UO, 6)])
else:
    HHHH = np.linspace(2, 6, N)

xyz = np.column_stack((xyz, HHHH))

kk = 0
XYZ = []

for k in range(N):  # 求圆内
    if ((xyz[k, 0]) ** 2 + (xyz[k, 1] - 250) ** 2) <= 350**2:
        XYZ.append([xyz[k, 0], xyz[k, 1], xyz[k, 2]])
        kk += 1

XYZ = np.array(XYZ)
NN = XYZ.shape[0]

for k in range(NN):
    XYZ[k, 2] = (XYZ[k, 0] ** 2 + XYZ[k, 1] ** 2 - 100**2) / (600**2 - 100**2) * 4 + 2

XYZZ = (roundn(XYZ[:, 2], -3) - 2) * 3 / 2 + 2
SD1 = np.unique(XYZZ)
SD2 = np.unique(roundn(XYZ[:, 2], -3))
ST = [9, 10.5, 12, 13.5, 15]
D = [306, 337, 0, 31, 61, 92, 122, 153, 184, 214, 245, 275]
N = XYZ.shape[0]
l = 5.87
w = 5.87

x0 = 0
y0 = 0

e5 = 0.92
A, B = SUN(12, 0)
e1 = f1(XYZ, l, w, N, A, B, x0, y0)
e2, e22 = f2(XYZ, N, x0, y0, A, B)
e3, e33 = f3(XYZ, N, x0, y0)
e4, e44 = f4(XYZ, l, w, N, A, B, x0, y0)

e = e22 * e33 * e44 * e1 * e5

# 绘图
# plt.figure(1, figsize=(10, 6))
# qq = np.arange(1, len(e) + 1)  # 根据实际数据长度创建索引
# plt.bar(qq, e, width=0.25)
# plt.ylim(0.3, 1)
# plt.grid(True)
# plt.xlabel("定日镜序号")
# plt.ylabel("平均光学效率")
# plt.axvline(x=len(e), color="r")
# plt.tight_layout()

# plt.figure(2, figsize=(10, 6))
# plt.bar(qq[:45], e[:45], width=0.25)
# plt.ylim(0.3, 1)
# plt.grid(True)
# plt.xlabel("定日镜序号")
# plt.ylabel("平均光学效率")
# plt.axvline(x=45.5, color="r")
# plt.tight_layout()

# plt.figure(3, figsize=(10, 6))
XXYYZZ = np.column_stack((XYZ[:, 0], XYZ[:, 1] - 250, XYZ[:, 2]))
# plt.scatter(XXYYZZ[:, 0], XXYYZZ[:, 1], s=100, marker=".")
# plt.grid(True)
# plt.xlabel("x方向")
# plt.ylabel("y方向")
# plt.tight_layout()

# plt.figure(4, figsize=(9, 6))
# oo = np.arange(1, 41)
# plt.bar(oo, SD1[:40] if len(SD1) >= 40 else SD1)
# plt.grid(True)
# plt.xlabel("同心圆序号")
# plt.ylabel("定日镜宽度(高度）/(m)")
# plt.axvline(x=41, color="r")
# plt.axhline(y=8, color="r")
# plt.xlim(0, 41)
# plt.ylim(0, 10)
# plt.tight_layout()

# plt.figure(5, figsize=(9, 6))
# plt.bar(oo, SD2[:40] if len(SD2) >= 40 else SD2)
# plt.grid(True)
# plt.xlabel("同心圆序号")
# plt.ylabel("定日镜安装高度/(m)")
# plt.axvline(x=41, color="r")
# plt.axhline(y=6, color="r")
# plt.xlim(0, 41)
# plt.ylim(0, 10)
# plt.tight_layout()

# plt.figure(6, figsize=(10, 8))
# ax = plt.axes(projection="3d")
# hhh = np.arange(0, 11)
# ax.scatter3D(XXYYZZ[:, 0], XXYYZZ[:, 1], XXYYZZ[:, 2], marker=".")
# ax.plot3D(np.zeros(11), -250 * np.ones(11), hhh, "r", linewidth=1.5)
# ax.set_xlabel("x方向")
# ax.set_ylabel("y方向")
# ax.set_zlabel("z方向")
# plt.grid(True)

plt.figure(7, figsize=(10, 8))
ax = plt.axes(projection="3d")
cir = 50
scatter = ax.scatter3D(XXYYZZ[:, 0], XXYYZZ[:, 1], e, s=cir, c=e, marker=".")
ax.set_xlabel("x方向")
ax.set_ylabel("y方向")
plt.colorbar(scatter)

plt.show()
