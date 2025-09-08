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
DT = 0.05
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

tCalculateRange = npy.arange(0.0, 100.0, DT, dtype=npy.float32)


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
def calculateIntersection(posMissile: Vector3) -> List[Vector3]:
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


@numba.njit()
def calculateCheckpoints(t: float) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t)
    points = []
    points_cylinder = calculateIntersection(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    points_perp = calculatePerpendicularIntersection(posNowMissile)
    for p in points_perp:
        points.append(p)
    return points


@numba.njit()
def checkLineIntersectSphere(
    linePoint1: Vector3, linePoint2: Vector3, sphereCenter: Vector3, sphereRadius: float
) -> bool:
    return distancePoint2Line(linePoint1, linePoint2, sphereCenter) <= sphereRadius


@numba.njit()
def calculateMultipleFYMaskedTime(
    angle1_deg: float,
    speedFY1: float,
    tRelease1: float,
    tDelay1: float,
    angle2_deg: float,
    speedFY2: float,
    tRelease2: float,
    tDelay2: float,
    angle3_deg: float,
    speedFY3: float,
    tRelease3: float,
    tDelay3: float,
) -> Tuple[float, List[float]]:
    angle1 = npy.deg2rad(angle1_deg)
    angle2 = npy.deg2rad(angle2_deg)
    angle3 = npy.deg2rad(angle3_deg)
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
    angle_deg: float,
    speedFY: float,
    tRelease: float,
    tDelay: float,
    posFYInitial: Vector3,
) -> float:
    angle = npy.deg2rad(angle_deg)
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
        angle1_deg,
        speedFY1,
        tRelease1,
        tDelay1,
        angle2_deg,
        speedFY2,
        tRelease2,
        tDelay2,
        angle3_deg,
        speedFY3,
        tRelease3,
        tDelay3,
    ) = params
    return calculateMultipleFYMaskedTime(
        angle1_deg,
        speedFY1,
        tRelease1,
        tDelay1,
        angle2_deg,
        speedFY2,
        tRelease2,
        tDelay2,
        angle3_deg,
        speedFY3,
        tRelease3,
        tDelay3,
    )


leftBounds = [*[0, 70, 0, 0.5] * 3]
rightBounds = [*[360, 140, 67, 20.0] * 3]

TOTAL_COUNT = 800

progressBarState = tqdm(total=TOTAL_COUNT, desc="GA Progress")

currentMaxCoverTime = [-1]


def onProgressNext(gaInstance: GA):
    progressBarState.update(1)
    if not gaInstance.generation_best_Y:
        return
    currentMaxCoverTime[0] = max(
        currentMaxCoverTime[0], -(gaInstance.generation_best_Y[-1])
    )
    progressBarState.set_postfix({"best": f"{currentMaxCoverTime[0]:.2f}s"})


class ProgressedGA(GA):
    def crossover(self):
        onProgressNext(self)
        return super().crossover()


set_run_mode(objectiveCalculateMultipleFYMaskedTime, "multithreading")
gaObject = ProgressedGA(
    func=objectiveCalculateMultipleFYMaskedTime,
    n_dim=12,
    size_pop=1000,
    prob_mut=0.01,
    max_iter=TOTAL_COUNT,
    lb=leftBounds,
    ub=rightBounds,
    precision=1e-7,
)
# import torch

# print(torch.cuda.is_available())
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# gaObject.to(device)
bestParams, bestAnswer = gaObject.run()
progressBarState.close()


print(f"best params:{bestParams}")
print(f"best answer:{bestAnswer}")

import pandas as pd

(
    angle1_deg,
    speedFY1,
    tRelease1,
    tDelay1,
    angle2_deg,
    speedFY2,
    tRelease2,
    tDelay2,
    angle3_deg,
    speedFY3,
    tRelease3,
    tDelay3,
) = bestParams

params_list: List[Tuple[float, float, float, float, Vector3]] = [
    (angle1_deg, speedFY1, tRelease1, tDelay1, posFY1),
    (angle2_deg, speedFY2, tRelease2, tDelay2, posFY2),
    (angle3_deg, speedFY3, tRelease3, tDelay3, posFY3),
]

results = []
for index, params in enumerate(params_list):
    angle_deg, speed, tRelease, tDelay, pos_initial = params
    angle = npy.deg2rad(angle_deg)
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
            "无人机运动方向 (deg)": angle_deg,
            "无人机运动速度 (m/s)": speed,
            "烟幕干扰弹投放点的x坐标 (m)": posRelease[0],
            "烟幕干扰弹投放点的y坐标 (m)": posRelease[1],
            "烟幕干扰弹投放点的z坐标 (m)": posRelease[2],
            "烟幕干扰弹起爆点的x坐标 (m)": posDetonate[0],
            "烟幕干扰弹起爆点的y坐标 (m)": posDetonate[1],
            "烟幕干扰弹起爆点的z坐标 (m)": posDetonate[2],
            "有效干扰时长 (s)": -calculateSingleFYMaskedTime(
                angle_deg, speed, tRelease, tDelay, pos_initial
            ),
        }
    )
df = pd.DataFrame(results)
output_path = f"A题/result.a4.v3-{-bestAnswer[0]:.4f}-{datetime.datetime.now().strftime('%H%M%S')}.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig", mode="w")

print(f"结果已保存到 {output_path}")


def drawMultipleFYPathImage(params: List[float]):
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    import matplotlib.pyplot as pyplot
    from matplotlib.patches import Patch

    (
        angle1_deg,
        speedFY1,
        tRelease1,
        tDelay1,
        angle2_deg,
        speedFY2,
        tRelease2,
        tDelay2,
        angle3_deg,
        speedFY3,
        tRelease3,
        tDelay3,
    ) = params

    angles_rad = npy.deg2rad([angle1_deg, angle2_deg, angle3_deg])
    speeds: List[float] = [speedFY1, speedFY2, speedFY3]
    tReleases: List[float] = [tRelease1, tRelease2, tRelease3]
    tDelays: List[float] = [tDelay1, tDelay2, tDelay3]
    posFYs: List[Vector3] = [posFY1, posFY2, posFY3]

    tDetonates = npy.array(tReleases) + npy.array(tDelays)
    directions: List[Vector3] = [
        npy.array([npy.cos(ang), npy.sin(ang), 0.0]) for ang in angles_rad
    ]

    posReleases: List[Vector3] = [
        posFYs[i] + speeds[i] * tReleases[i] * directions[i] for i in range(3)
    ]
    posDetonates: List[Vector3] = [
        posReleases[i]
        + speeds[i] * tDelays[i] * directions[i]
        - 0.5 * G * tDelays[i] ** 2 * npy.array([0.0, 0.0, 1.0])
        for i in range(3)
    ]
    tDetonatesArray = npy.array(tDetonates)
    posDetonatesArray = npy.array(posDetonates)

    @numba.njit(fastmath=True)
    def checkCoveredForPlot(t: float) -> bool:
        posMissileInstant = getMissilePosition(t)

        checkpoints_list = calculateCheckpoints(t)
        if not checkpoints_list:
            return False
        availableCloudCenters = []
        for i in range(3):
            if tDetonatesArray[i] <= t <= tDetonatesArray[i] + tCloud:
                availableCloudCenters.append(
                    getCloudPosition(t, posDetonatesArray[i], tDetonatesArray[i])
                )

        if not availableCloudCenters:
            return False

        isAllCovered = True
        for point in checkpoints_list:
            isPointBlocked = False
            for cloudCenter in availableCloudCenters:
                if distancePoint2Line(posMissileInstant, point, cloudCenter) <= rCloud:
                    isPointBlocked = True
                    break
            if not isPointBlocked:
                isAllCovered = False
                break
        return isAllCovered

    fig = pyplot.figure(figsize=(18, 14))
    axis = fig.add_subplot(111, projection="3d")
    pyplot.rcParams["font.sans-serif"] = ["SimHei"]
    pyplot.rcParams["axes.unicode_minus"] = False

    DRAW_DT = 0.1
    tMax = 20000.0 / speedMissile
    tIterator = npy.arange(0, tMax, DRAW_DT)

    trajMissile = npy.array([getMissilePosition(t) for t in tIterator])
    isCoveredStatus = npy.array(
        [checkCoveredForPlot(t) for t in tqdm(tIterator, desc="计算导弹遮蔽状态")]
    )

    pointsTrajMissile = trajMissile.reshape(-1, 1, 3)
    segmentsTrajMissile = npy.concatenate(
        [pointsTrajMissile[:-1], pointsTrajMissile[1:]], axis=1
    )
    colorsTrajMissile = npy.where(isCoveredStatus[:-1], "black", "red")

    axis.add_collection(
        Line3DCollection(
            segmentsTrajMissile,
            colors=colorsTrajMissile,
            linewidths=2,
            label="导弹轨迹",
        )
    )

    drone_colors = ["blue", "green", "purple"]
    for i in range(3):
        trajFY_t = npy.arange(0, tReleases[i] + DRAW_DT, DRAW_DT)
        trajFY = npy.array(
            [posFYs[i] + speeds[i] * t * directions[i] for t in trajFY_t]
        )
        axis.plot(
            trajFY[:, 0],
            trajFY[:, 1],
            trajFY[:, 2],
            color=drone_colors[i],
            linestyle="--",
            label=f"无人机{i+1}轨迹",
        )

        trajDecoy_t = npy.arange(0, tDelays[i] + DRAW_DT, DRAW_DT)
        trajDecoy = npy.array(
            [
                posReleases[i]
                + speeds[i] * t * directions[i]
                - 0.5 * G * t**2 * npy.array([0.0, 0.0, 1.0])
                for t in trajDecoy_t
            ]
        )
        axis.plot(
            trajDecoy[:, 0],
            trajDecoy[:, 1],
            trajDecoy[:, 2],
            color=drone_colors[i],
            linestyle=":",
            label=f"干扰弹{i+1}轨迹",
        )

        trajSmoke_t = npy.arange(
            tDetonates[i], tDetonates[i] + tCloud + DRAW_DT, DRAW_DT
        )
        trajSmoke = npy.array(
            [getCloudPosition(t, posDetonates[i], tDetonates[i]) for t in trajSmoke_t]
        )
        axis.plot(
            trajSmoke[:, 0],
            trajSmoke[:, 1],
            trajSmoke[:, 2],
            color="orange",
            linestyle="-",
            label=f"烟雾{i+1}下沉" if i == 0 else "",
        )
        u, v = npy.linspace(0, 2 * npy.pi, 20), npy.linspace(0, npy.pi, 20)
        for center in trajSmoke[::20]:  # 每隔一段距离画一个球
            x = center[0] + rCloud * npy.outer(npy.cos(u), npy.sin(v))
            y = center[1] + rCloud * npy.outer(npy.sin(u), npy.sin(v))
            z = center[2] + rCloud * npy.outer(npy.ones(npy.size(u)), npy.cos(v))
            axis.plot_surface(x, y, z, color="gray", alpha=0.08, linewidth=0)

        axis.scatter(
            *posReleases[i],
            color=drone_colors[i],
            marker="^",
            s=80,
            label=f"投放点{i+1}",
        )
        axis.scatter(
            *posDetonates[i],
            color=drone_colors[i],
            marker="*",
            s=120,
            label=f"爆炸点{i+1}",
        )

    axis.scatter(*posMissile, color="red", marker="s", s=100, label="导弹发射点")
    axis.scatter(*posRealTarget, color="black", marker="X", s=100, label="真实目标")

    legend_elements = [
        pyplot.Line2D([0], [0], color="red", lw=2, label="导弹轨迹 (未遮蔽)"),
        pyplot.Line2D([0], [0], color="black", lw=2, label="导弹轨迹 (被遮蔽)"),
        Patch(facecolor="gray", alpha=0.3, label="烟幕云"),
        pyplot.Line2D([0], [0], color="orange", lw=2, label="烟雾下沉轨迹"),
        pyplot.Line2D([0], [0], color="blue", linestyle="--", label="无人机1轨迹"),
        pyplot.Line2D([0], [0], color="green", linestyle="--", label="无人机2轨迹"),
        pyplot.Line2D([0], [0], color="purple", linestyle="--", label="无人机3轨迹"),
        pyplot.Line2D(
            [0],
            [0],
            marker="^",
            color="w",
            label="投放点",
            markerfacecolor="k",
            markersize=10,
        ),
        pyplot.Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            label="爆炸点",
            markerfacecolor="k",
            markersize=12,
        ),
    ]
    axis.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.05, 1))

    axis.set_xlabel("X (m)")
    axis.set_ylabel("Y (m)")
    axis.set_zlabel("Z (m)")
    axis.set_title("三无人机协同遮蔽三维轨迹示意图")

    all_points = npy.vstack(posReleases + posDetonates)
    center = npy.mean(all_points, axis=0)
    max_range = npy.max(npy.max(all_points, axis=0) - npy.min(all_points, axis=0))

    axis.set_xlim(center[0] - max_range, center[0] + max_range)
    axis.set_ylim(center[1] - max_range, center[1] + max_range)
    axis.set_zlim(center[2] - max_range, center[2] + max_range)

    axis.set_box_aspect((1, 1, 1))
    pyplot.tight_layout()
    pyplot.show()


drawMultipleFYPathImage(bestParams)
