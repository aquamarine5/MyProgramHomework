import datetime
import sys
from time import time
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Optional, Tuple
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm
from sko.GA import GA
from sko.PSO import PSO
from sko.tools import set_run_mode

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
DT = 0.1
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

tCalculateRange = npy.arange(0.0, 66.0, DT, dtype=npy.float32)


@numba.njit()
def getMissilePosition(t: float) -> Vector3:
    return posMissile + speedMissile * t * directionMissile


@numba.njit()
def getCloudPosition(t: float, posDetonate: Vector3, tDetonate: float) -> Vector3:
    return npy.array(
        [posDetonate[0], posDetonate[1], posDetonate[2] - speedCloud * (t - tDetonate)]
    )


@numba.njit()
def distancePoint2Line(
    linePoint1: Vector3, linePoint2: Vector3, targetPoint: Vector3
) -> float:
    lineVec: Vector3 = linePoint2 - linePoint1
    pointVec: Vector3 = targetPoint - linePoint1
    s = npy.dot(lineVec, pointVec) / npy.dot(lineVec, lineVec)
    s_clamped = max(0.0, min(s, 1.0))
    closest = linePoint1 + s_clamped * lineVec
    return npy.linalg.norm(targetPoint - closest)


@numba.jit()
def calculate_intersection_with_cylinder(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)
    pointsIntersection = []
    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]
        if x < 0:
            pointsIntersection.append(
                npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
            )
        if x > 0:
            pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部
    return pointsIntersection


@numba.njit()
def calculate_perpendicular_plane_intersection(posMissile: Vector3) -> List[Vector3]:
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


@numba.njit()
def calculateCheckpoints(t: float) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t)
    # Use a Numba typed list for compatibility
    points = []
    # Manually append items from the first function call
    points_cylinder = calculate_intersection_with_cylinder(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    # Manually append items from the second function call
    points_perp = calculate_perpendicular_plane_intersection(posNowMissile)
    for p in points_perp:
        points.append(p)
    return points


# better way to write this function
@numba.njit()
def checkLineIntersectSphere(
    linePoint1: Vector3, linePoint2: Vector3, sphereCenter: Vector3, sphereRadius: float
) -> bool:
    return distancePoint2Line(linePoint1, linePoint2, sphereCenter) <= sphereRadius


@numba.njit()
def calculateMultipleFYMaskedTime(
    angle1: float,
    speedFY1: float,
    tRelease1: float,
    tDelay1: float,
    angle2: float,
    speedFY2: float,
    tRelease2: float,
    tDelay2: float,
    angle3: float,
    speedFY3: float,
    tRelease3: float,
    tDelay3: float,
) -> Tuple[float, List[float]]:
    tDetonateList: NDArray[npy.float32] = npy.array(
        [
            tRelease1 + tDelay1,
            tRelease2 + tDelay2,
            tRelease3 + tDelay3,
        ]
    )
    directionFYList: List[Vector3] = [
        npy.array([npy.cos(angle1), npy.sin(angle1), 0.0]),
        npy.array([npy.cos(angle2), npy.sin(angle2), 0.0]),
        npy.array([npy.cos(angle3), npy.sin(angle3), 0.0]),
    ]
    posReleaseList: List[Vector3] = [
        posFY1 + speedFY1 * tRelease1 * directionFYList[0],
        posFY2 + speedFY2 * tRelease2 * directionFYList[1],
        posFY3 + speedFY3 * tRelease3 * directionFYList[2],
    ]
    posDetonateList: List[Vector3] = [
        posReleaseList[0]
        + tDelay1 * speedFY1 * directionFYList[0]
        - 0.5 * G * tDelay1**2 * npy.array([0.0, 0.0, 1.0]),
        posReleaseList[1]
        + tDelay2 * speedFY2 * directionFYList[1]
        - 0.5 * G * tDelay2**2 * npy.array([0.0, 0.0, 1.0]),
        posReleaseList[2]
        + tDelay3 * speedFY3 * directionFYList[2]
        - 0.5 * G * tDelay3**2 * npy.array([0.0, 0.0, 1.0]),
    ]
    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        posMissileInstant: Vector3 = getMissilePosition(instant)
        availableCloudCenterList: List[Vector3] = []
        if tDetonateList[0] <= instant <= tDetonateList[0] + tCloud:
            availableCloudCenterList.append(
                getCloudPosition(instant, posDetonateList[0], tDetonateList[0])
            )
        if tDetonateList[1] <= instant <= tDetonateList[1] + tCloud:
            availableCloudCenterList.append(
                getCloudPosition(instant, posDetonateList[1], tDetonateList[1])
            )
        if tDetonateList[2] <= instant <= tDetonateList[2] + tCloud:
            availableCloudCenterList.append(
                getCloudPosition(instant, posDetonateList[2], tDetonateList[2])
            )

        if not availableCloudCenterList:
            continue

        isCovered = True
        for point in calculateCheckpoints(instant):
            isBlocked = False
            for cloudCenter in availableCloudCenterList:
                if checkLineIntersectSphere(
                    posMissileInstant, point, cloudCenter, rCloud
                ):
                    isBlocked = True
                    break
            if not isBlocked:
                isCovered = False
                break
        isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


@numba.njit()
def calculateSingleFYMaskedTime(
    angle: float,
    speedFY: float,
    tRelease: float,
    tDelay: float,
    posFYInitial: Vector3,
) -> float:
    tDetonate = tRelease + tDelay
    directionFY: Vector3 = npy.array([npy.cos(angle), npy.sin(angle), 0.0])
    posRelease: Vector3 = posFYInitial + speedFY * tRelease * directionFY
    posDetonate: Vector3 = (
        posRelease
        + tDelay * speedFY * directionFY
        - 0.5 * G * tDelay**2 * npy.array([0.0, 0.0, 1.0])
    )
    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        posMissileInstant: Vector3 = getMissilePosition(instant)
        if tDetonate <= instant <= tDetonate + tCloud:
            availableCloudCenter = getCloudPosition(instant, posDetonate, tDetonate)
            isCovered = True
            for point in calculateCheckpoints(instant):
                if not checkLineIntersectSphere(
                    posMissileInstant, point, availableCloudCenter, rCloud
                ):
                    isCovered = False
                    break
            isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


def objectiveCalculateMultipleFYMaskedTime(params: List[float]) -> float:
    (
        angle1,
        speedFY1,
        tRelease1,
        tDelay1,
        angle2,
        speedFY2,
        tRelease2,
        tDelay2,
        angle3,
        speedFY3,
        tRelease3,
        tDelay3,
    ) = params
    return calculateMultipleFYMaskedTime(
        angle1,
        speedFY1,
        tRelease1,
        tDelay1,
        angle2,
        speedFY2,
        tRelease2,
        tDelay2,
        angle3,
        speedFY3,
        tRelease3,
        tDelay3,
    )


leftBounds = [*[0, 70, 0, 0.5] * 3]
rightBounds = [*[2 * npy.pi, 140, 67, 20.0] * 3]

TOTAL_COUNT = 10000

progressBarState = tqdm(total=TOTAL_COUNT, desc="GA Progress")

currentMaxCoverTime = [-1]


def onProgressNext(psoInstance: PSO):
    progressBarState.update(1)
    if isinstance(psoInstance.gbest_y, float):
        currentMaxCoverTime[0] = psoInstance.gbest_y
    else:
        currentMaxCoverTime[0] = psoInstance.gbest_y[0]
    progressBarState.set_postfix({"best": f"{-currentMaxCoverTime[0]:.2f}s"})


class ProgressedPSO(PSO):
    def recorder(self):  # -> Any:
        onProgressNext(self)
        return super().recorder()


set_run_mode(objectiveCalculateMultipleFYMaskedTime, "multithreading")
psoObject = ProgressedPSO(
    func=objectiveCalculateMultipleFYMaskedTime,
    n_dim=12,
    pop=400,
    max_iter=TOTAL_COUNT,
    lb=leftBounds,
    ub=rightBounds,
    w=0.2,
    c1=1.5,
    c2=3,
)
# import torch

# print(torch.cuda.is_available())
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# gaObject.to(device)
bestParams, bestAnswer = psoObject.run()
progressBarState.close()
print(f"best params:{bestParams}")
print(f"best answer:{bestAnswer}")

import pandas as pd

# Extract best parameters
(
    angle1,
    speedFY1,
    tRelease1,
    tDelay1,
    angle2,
    speedFY2,
    tRelease2,
    tDelay2,
    angle3,
    speedFY3,
    tRelease3,
    tDelay3,
) = bestParams

params_list = [
    (angle1, speedFY1, tRelease1, tDelay1, posFY1),
    (angle2, speedFY2, tRelease2, tDelay2, posFY2),
    (angle3, speedFY3, tRelease3, tDelay3, posFY3),
]
import matplotlib.pyplot as plt

plt.title(f"PSO:{-bestAnswer[0]:.2f}s")
plt.plot(psoObject.gbest_y_hist)
plt.show()

results = []
for index, params in enumerate(params_list):
    angle, speed, tRelease, tDelay, pos_initial = params
    direction: Vector3 = npy.array([npy.cos(angle), npy.sin(angle), 0.0])
    posRelease: Vector3 = pos_initial + speed * tRelease * direction
    v_release: Vector3 = speed * direction
    posDetonate: Vector3 = (
        posRelease
        + v_release * tDelay
        - 0.5 * G * tDelay**2 * npy.array([0.0, 0.0, 1.0])
    )
    results.append(
        {
            "无人机编号": f"FY{index+1}",
            "无人机运动方向": angle,
            "无人机运动速度 (m/s)": speed,
            "烟幕干扰弹投放点的x坐标 (m)": posRelease[0],
            "烟幕干扰弹投放点的y坐标 (m)": posRelease[1],
            "烟幕干扰弹投放点的z坐标 (m)": posRelease[2],
            "烟幕干扰弹起爆点的x坐标 (m)": posDetonate[0],
            "烟幕干扰弹起爆点的y坐标 (m)": posDetonate[1],
            "烟幕干扰弹起爆点的z坐标 (m)": posDetonate[2],
            "有效干扰时长 (s)": -calculateSingleFYMaskedTime(
                angle, speed, tRelease, tDelay, pos_initial
            ),
        }
    )
df = pd.DataFrame(results)
output_path = f"A题/result.a4.v4-{-bestAnswer[0]:.4f}-{datetime.datetime.now().strftime('%H%M%S')}.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig", mode="w")

print(f"结果已保存到 {output_path}")
