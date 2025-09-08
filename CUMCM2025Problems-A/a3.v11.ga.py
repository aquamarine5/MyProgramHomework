import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from scipy.optimize._optimize import OptimizeResult
from sympy import im
from tqdm import tqdm

Vector3 = NDArray[npy.float64]


posMissile: Vector3 = npy.array([20000.0, 0.0, 2000.0])
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])
directionMissile: Vector3 = (posMissileTarget - posMissile) / npy.linalg.norm(
    posMissileTarget - posMissile
)
vMissile = speedMissile * directionMissile
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
rRealTarget = 7
hRealTarget = 10
posFY1: Vector3 = npy.array([17800.0, 0.0, 1800.0])
posFY2: Vector3 = npy.array([12000.0, 1400.0, 1400.0])
posFY3: Vector3 = npy.array([6000.0, -3000.0, 700.0])
speedFYMin = 70.0
speedFYMax = 140.0
G = 9.8
DT = 0.002
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

tCalculateRange = npy.arange(0.0, 100.0, DT, dtype=npy.float32)


@numba.jit()
def getMissilePosition(t: float) -> Vector3:
    return posMissile + speedMissile * t * directionMissile


@numba.jit()
def getCloudPosition(t: float, posDetonate: Vector3, tDetonate: float) -> Vector3:
    return npy.array(
        [posDetonate[0], posDetonate[1], posDetonate[2] - speedCloud * (t - tDetonate)]
    )


@numba.jit()
def distancePoint2Line(
    linePoint1: Vector3, linePoint2: Vector3, targetPoint: Vector3
) -> float:
    lineVec: Vector3 = linePoint2 - linePoint1
    pointVec: Vector3 = targetPoint - linePoint1
    s = npy.dot(lineVec, pointVec) / npy.dot(lineVec, lineVec)
    s_clamped = max(0.0, min(s, 1.0))
    closest = linePoint1 + s_clamped * lineVec
    return npy.linalg.norm(targetPoint - closest)


@numba.njit()
def calculateIntersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)
    pointsIntersection = []
    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]
        if x < 0:
            pointsIntersection.append(npy.array([x, y, posRealTarget[2] + hRealTarget]))
        if x > 0:
            pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))
    return pointsIntersection


@numba.njit()
def calculatePerpendicularIntersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)
    directionPerpendicular = npy.array([-directionMissile[1], directionMissile[0]])
    pointsIntersection = []
    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionPerpendicular[0]
        y = posRealTarget[1] + sign * rRealTarget * directionPerpendicular[1]

        pointsIntersection.append(npy.array([x, y, posRealTarget[2] + hRealTarget]))
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))
    return pointsIntersection


@numba.jit()
def calculateCheckpoints(t: float) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t)
    # Use a Numba typed list for compatibility
    points = []
    # Manually append items from the first function call
    points_cylinder = calculateIntersection(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    # Manually append items from the second function call
    points_perp = calculatePerpendicularIntersection(posNowMissile)
    for p in points_perp:
        points.append(p)
    return points


# better way to write this function
@numba.jit()
def checkLineIntersectSphere(
    linePoint1: Vector3, linePoint2: Vector3, sphereCenter: Vector3, sphereRadius: float
) -> bool:
    return distancePoint2Line(linePoint1, linePoint2, sphereCenter) <= sphereRadius


@numba.njit()
def calculateSingleCloudTime(
    theta: float, speedFY: float, tRelease: float, tDelay: float
) -> float:
    tDetonate = tRelease + tDelay
    directionFY1: Vector3 = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    posFY1Release = posFY1 + speedFY * tRelease * directionFY1
    posDetonate = (
        posFY1Release
        + tDelay * speedFY * directionFY1
        - 0.5 * G * tDelay**2 * npy.array([0.0, 0.0, 1.0])
    )

    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        if not (tDetonate <= instant <= tDetonate + tCloud):
            isMaskedList[index] = 0
            continue

        posMissileInstant = getMissilePosition(instant)
        checkpoints = calculateCheckpoints(instant)
        isCovered = True
        posCloudInstant = getCloudPosition(instant, posDetonate, tDetonate)

        for point in checkpoints:
            if not checkLineIntersectSphere(
                posMissileInstant, point, posCloudInstant, rCloud
            ):
                isCovered = False
                break
        isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


@numba.njit()
def calculateMultipleCloudTime(
    theta: float,
    speedFY: float,
    tRelease1: float,
    tDelay1: float,
    tSpan12: float,
    tDelay2: float,
    tSpan13: float,
    tDelay3: float,
) -> float:
    tReleaseList: NDArray[npy.float32] = npy.array(
        [tRelease1, tRelease1 + tSpan12, tRelease1 + tSpan13]
    )
    tDelayList: NDArray[npy.float32] = npy.array([tDelay1, tDelay2, tDelay3])
    tDetonateList: NDArray[npy.float32] = tReleaseList + tDelayList
    directionFY1: Vector3 = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    posFY1ReleaseList: NDArray[npy.float32] = npy.zeros((3, 3))
    posDetonateList: NDArray[npy.float32] = npy.zeros((3, 3))
    for i in range(3):
        posFY1ReleaseList[i, :] = posFY1 + speedFY * tReleaseList[i] * directionFY1
        posDetonateList[i, :] = (
            posFY1ReleaseList[i, :]
            + tDelayList[i] * speedFY * directionFY1
            - 0.5 * G * tDelayList[i] ** 2 * npy.array([0.0, 0.0, 1.0])
        )

    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        posMissileInstant = getMissilePosition(instant)
        checkpoints = calculateCheckpoints(instant)
        posCloudsList = [
            getCloudPosition(instant, posDetonateList[i], tDetonateList[i])
            for i in range(3)
        ]
        isCovered = True
        for point in checkpoints:
            isBlocked = False
            for i in range(3):
                if tDetonateList[i] <= instant <= tDetonateList[i] + tCloud:
                    if checkLineIntersectSphere(
                        posMissileInstant, point, posCloudsList[i], rCloud
                    ):
                        isBlocked = True
                        break
            if not isBlocked:
                isCovered = False
                break
        isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


def objectiveCalculateMultipleCloudTime(params):
    theta, speedFY, tRelease1, tDelay1, tSpan12, tDelay2, tSpan13, tDelay3 = params
    return calculateMultipleCloudTime(
        theta,
        speedFY,
        tRelease1,
        tDelay1,
        tSpan12,
        tDelay2,
        tSpan13,
        tDelay3,
    )


TOTAL_COUNT = 800

progressBarState = tqdm(total=TOTAL_COUNT, desc="GA Progress")

from sko.GA import GA
from sko.tools import set_run_mode

currentMaxCoverTime = [-1]

set_run_mode(objectiveCalculateMultipleCloudTime, "multithreading")


def onProgressNext(gaInstance: GA):
    progressBarState.update(1)
    if not gaInstance.generation_best_Y:
        return
    currentMaxCoverTime[0] = max(
        currentMaxCoverTime[0], -(gaInstance.generation_best_Y[-1])
    )
    progressBarState.set_postfix({"best": f"{currentMaxCoverTime[0]:.4f}s"})


class ProgressedGA(GA):
    def crossover(self):
        onProgressNext(self)
        return super().crossover()


lb = [0, 70, 0, 0.1, 1, 0.1, 1, 0.1]
ub = [0.5, 140, 5, 3, 10, 3, 20, 3]
gaObject = ProgressedGA(
    objectiveCalculateMultipleCloudTime,
    prob_mut=0.01,
    lb=lb,
    ub=ub,
    size_pop=200,
    max_iter=TOTAL_COUNT,
    n_dim=8,
)

# import torch

# print(torch.cuda.is_available())
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# gaObject.to(device)
bestParams, bestAnswer = gaObject.run()

print("Best parameters found:", bestParams)
print("Maximum masked time:", -bestAnswer)
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.patches import Patch


plt.plot(gaObject.generation_best_Y)
plt.show()
from datetime import datetime

# 从 bestParams 中解包优化结果
theta, speedFY, tRelease1, tDelay1, tSpan12, tDelay2, tSpan13, tDelay3 = bestParams

# 计算无人机运动方向
directionFY = npy.array([npy.cos(theta), npy.sin(theta), 0.0])

tReleaseList = npy.array([tRelease1, tRelease1 + tSpan12, tRelease1 + tSpan13])
tDelayList = npy.array([tDelay1, tDelay2, tDelay3])

# 准备存储结果的列表
results = []

# 循环计算每个干扰弹的数据
for i in range(3):
    # 计算投放点坐标
    posRelease = posFY1 + speedFY * tReleaseList[i] * directionFY

    # 计算起爆点坐标
    posDetonate = (
        posRelease
        + tDelayList[i] * speedFY * directionFY
        - 0.5 * G * tDelayList[i] ** 2 * npy.array([0.0, 0.0, 1.0])
    )
    # 将结果存入字典
    results.append(
        {
            "无人机运动方向": f"({directionFY[0]:.4f}, {directionFY[1]:.4f}, {directionFY[2]:.4f})",
            "无人机运动速度 (m/s)": speedFY,
            "烟幕干扰弹编号": i + 1,
            "烟幕干扰弹投放点的x坐标 (m)": posRelease[0],
            "烟幕干扰弹投放点的y坐标 (m)": posRelease[1],
            "烟幕干扰弹投放点的z坐标 (m)": posRelease[2],
            "烟幕干扰弹起爆点的x坐标 (m)": posDetonate[0],
            "烟幕干扰弹起爆点的y坐标 (m)": posDetonate[1],
            "烟幕干扰弹起爆点的z坐标 (m)": posDetonate[2],
            "有效干扰时长 (s)": -bestAnswer,
        }
    )

# 创建 DataFrame
df = pd.DataFrame(results)

# 将第一行和第二行的“无人机运动方向”、“无人机运动速度”和“有效干扰时长”设置为空字符串，以匹配格式
for col in ["无人机运动方向", "无人机运动速度 (m/s)", "有效干扰时长 (s)"]:
    df.loc[1, col] = ""
    df.loc[2, col] = ""


# 生成文件名
timestamp = datetime.now().strftime("%H%M%S")
filename = f"result.a3.v11-{-bestAnswer[0]:.2f}s-{timestamp}.csv"

# 保存到 CSV 文件
df.to_csv(filename, index=False, encoding="utf-8-sig")

print(f"结果已保存到文件: {filename}")
