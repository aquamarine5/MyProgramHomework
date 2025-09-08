from warnings import deprecated
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numba
from numpy.typing import NDArray
import numpy as npy
import pandas as pds
import matplotlib.pyplot as mpl
from typing import List, Tuple
from tqdm import tqdm


Vector3 = NDArray[npy.float64]
Trajectory = List[Vector3]

posMissile: Vector3 = npy.array([20000.0, 0.0, 2000.0])
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])
posFakeTarget: Vector3 = posMissileTarget
directionMissile: Vector3 = (posMissileTarget - posMissile) / npy.linalg.norm(
    posMissileTarget - posMissile
)
vMissile = speedMissile * directionMissile
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
rRealTarget = 7
hRealTarget = 10
posFY1: Vector3 = npy.array([17800.0, 0.0, 1800.0])
speedFY1 = 120.0
directionFY1: Vector3 = (posFakeTarget - posFY1) / npy.linalg.norm(
    posFakeTarget - posFY1
)
vFY1 = speedFY1 * directionFY1

tRelease = 1.5
tDelay = 3.6
tDetonate = tRelease + tDelay
G = 9.8
posRelease: Vector3 = posFY1 + speedFY1 * tRelease * directionFY1
posDetonate: Vector3 = posRelease + speedFY1 * tDelay * directionFY1
posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0


DT = 0.0001


@numba.jit()
def getMissilePosition(t: float) -> Vector3:
    return posMissile + speedMissile * t * directionMissile


@numba.jit()
def getCloudPosition(t: float) -> Vector3:
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


@numba.jit()
def calculate_intersection_with_cylinder(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    # if npy.linalg.norm(v2directionMissile) == 0:
    #     return []

    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)

    pointsIntersection = []

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]

        pointsIntersection.append(
            npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        )
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部

    return pointsIntersection


@numba.jit()
def calculate_perpendicular_plane_intersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]

    # if npy.linalg.norm(v2directionMissile) == 0:
    #     return []

    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)

    directionPerpendicular = npy.array([-directionMissile[1], directionMissile[0]])

    pointsIntersection = []

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionPerpendicular[0]
        y = posRealTarget[1] + sign * rRealTarget * directionPerpendicular[1]

        pointsIntersection.append(
            npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        )
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部

    return pointsIntersection


@numba.jit()
def get6points(t: float) -> List[Vector3]:
    ax = (1400 * (20000 - 3000 * npy.sqrt(101) / 101 * t)) / (
        200 * npy.sqrt((20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2 + 40000)
    )
    ay = 200 + (1400) / (
        npy.sqrt(((20000 - 3000 * npy.sqrt(101) / 101 * t)) ** 2 + 40000)
    )
    az = 10
    bx = -ax
    by = 200 - (1400) / (
        npy.sqrt(((20000 - 3000 * npy.sqrt(101) / 101 * t)) ** 2 + 40000)
    )
    bz = 10
    cx = 1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    cy = 200 + 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / npy.sqrt(
        200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2
    )
    cz = 10
    dx = -1400 / npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    dy = 200 - 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / (
        npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    )
    dz = 10
    ex = (1400 * (20000 - 3000 * npy.sqrt(101) / 101 * t)) / (
        200 * npy.sqrt((20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2 + 200 * 200)
    )
    ey = 200 - (
        1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    )
    ez = 0
    fx = -ex
    fy = 200 + (
        1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    )
    fz = 0
    gx = 1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    gy = 200 + 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / (
        npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    )
    gz = 0
    hx = -gx
    hy = 200 - 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / (
        npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    )
    hz = 0
    result = []
    if ax < 0:
        result.append(npy.array([ax, ay, az]))
    if bx < 0:
        result.append(npy.array([bx, by, bz]))
    if ex > 0:
        result.append(npy.array([ex, ey, ez]))
    if fx > 0:
        result.append(npy.array([fx, fy, fz]))
    return [
        npy.array([cx, cy, cz]),
        npy.array([dx, dy, dz]),
        npy.array([gx, gy, gz]),
        npy.array([hx, hy, hz]),
    ]


def calculateCheckpoints(posMissile: Vector3) -> List[Vector3]:
    points = calculate_intersection_with_cylinder(posMissile)
    points += calculate_perpendicular_plane_intersection(posMissile)
    return points


@numba.jit()
def checkSmokeBetween(
    posMissile: Vector3, posCloud: Vector3, posCheckpoint: Vector3
) -> bool:
    return npy.dot(posCloud - posMissile, posCheckpoint - posMissile) > 0


@numba.jit()
def calculateCoverTimeV2() -> List[Tuple[float, float]]:
    tToMissile = posFakeTarget[0] - posMissile[0] / vMissile[0]
    tDetonate = tRelease + tDelay
    tStart = 0
    tEnd = min(tCloud, tToMissile - tDetonate)
    if tEnd <= 0:
        return [(0.0, 0.0)]
    intervals = []
    isInCover = False
    posRelease: Vector3 = posFY1 + vFY1 * tRelease
    posDetonate: Vector3 = npy.array(
        [
            posRelease[0] + vFY1[0] * tDelay,
            posRelease[1] + vFY1[1] * tDelay,
            posRelease[2] - 0.5 * G * (tDelay**2),
        ]
    )
    numSteps = int((tEnd - tStart) / DT)
    for i in range(numSteps + 1):
        currentTime = tStart + i * DT
        tMissile = tDetonate + currentTime
        posMissileNow = getMissilePosition(tMissile)
        posCloudNow = getCloudPosition(currentTime)
        allCovered = True
        for pt in get6points(currentTime):
            directionMissileToTarget = pt - posMissileNow
            directionMissileToTarget = directionMissileToTarget / npy.linalg.norm(
                directionMissileToTarget
            )
            distance = distancePoint2Line(
                posCloudNow, posMissileNow, directionMissileToTarget
            )
            isBetween = checkSmokeBetween(posMissileNow, posCloudNow, pt)
            inCloud = npy.linalg.norm(posMissileNow - posCloudNow) <= rCloud
            if not ((distance <= rCloud and isBetween) or inCloud):
                allCovered = False
                break
        if allCovered:
            if not isInCover:
                coverStart = currentTime
                isInCover = True
            intervals.append((coverStart, currentTime))
        else:
            isInCover = False
    if isInCover:
        intervals.append((coverStart, tEnd))
        isInCover = False
    return intervals


def checkCovered(t: float) -> bool:
    if t < tDetonate or t > tDetonate + tCloud:
        return False
    posNowMissile = getMissilePosition(t)
    checkpoints = calculateCheckpoints(posNowMissile)
    # checkpoints = get6points(t)
    posNowCloud = getCloudPosition(t)
    for checkpoint in checkpoints:
        d = distancePoint2Line(posNowMissile, checkpoint, posNowCloud)
        if (
            not (
                d <= rCloud
                and checkSmokeBetween(posNowMissile, posNowCloud, checkpoint)
            )
            or npy.linalg.norm(posNowMissile - posNowCloud) <= rCloud
        ):
            return False
    return True


# iterator = npy.arange(0, tDetonate + tCloud + 1, DT)

# # 添加进度条
# coveredData: NDArray[npy.int_] = npy.array(
#     [checkCovered(t) for t in tqdm(iterator, desc="Calculating coverage")]
# ).astype(int)

# changesData: NDArray[npy.int_] = npy.diff(coveredData)
# print(
#     "Changes in coverage status (1 for entry, -1 for exit):",
#     len(changesData),
#     changesData,
# )
# entriesList = iterator[1:][changesData == 1]
# exitsList = iterator[1:][changesData == -1]
# print("Entries:", iterator[1:])
# print("Exits:", exitsList)
# intervals = list(zip(entriesList, exitsList))
# print(intervals)
# tTotalCovered = sum([end - start for start, end in intervals])
# print(f"爆炸点位置: {posDetonate}")
# print(f"Total time covered: {tTotalCovered:.8f} seconds")

i = calculateCoverTimeV2()

print(i)
print(sum([end - start for start, end in i]))


def drawPathImage():
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Line3DCollection

    fig = mpl.figure(figsize=(12, 8))
    axis = fig.add_subplot(111, projection="3d")
    mpl.rcParams["font.sans-serif"] = ["SimHei"]
    mpl.rcParams["axes.unicode_minus"] = False
    DRAWDT = 0.1
    DRAW_ACCURATELY_DT = 0.01
    tMax = 20000.0 / speedMissile
    tIterator = npy.arange(0, tMax, DRAW_ACCURATELY_DT)

    trajMissile: Trajectory = npy.array([getMissilePosition(t) for t in tIterator])

    trajFY1: Trajectory = npy.array(
        [posFY1 + speedFY1 * t * directionFY1 for t in tIterator]
    )

    tDecoyIterator = npy.arange(tRelease, tDetonate, DRAWDT)
    trajDecoy: Trajectory = npy.array(
        [
            [
                posRelease[0] + speedFY1 * (t - tRelease) * directionFY1[0],
                posRelease[1],
                posRelease[2] - 0.5 * G * ((t - tRelease) ** 2),
            ]
            for t in tDecoyIterator
        ]
    )

    trajSmokeSink: Trajectory = npy.array(
        [getCloudPosition(t) for t in npy.arange(tDetonate, tDetonate + tCloud, DRAWDT)]
    )

    legendElements = [
        Patch(facecolor="gray", alpha=0.3, label="烟幕云覆盖区域"),
        mpl.Line2D([0], [0], color="red", lw=2, label="导弹轨迹（未遮蔽）"),
        mpl.Line2D([0], [0], color="yellow", lw=2, label="导弹轨迹（被遮蔽）"),
    ]

    def drawTrajectory(
        traj: Trajectory, label: str, color: str, linestyle: str = "-"
    ) -> None:
        legendElements.append(
            mpl.Line2D([0], [0], color=color, lw=2, linestyle=linestyle, label=label)
        )
        axis.plot(
            traj[:, 0],
            traj[:, 1],
            traj[:, 2],
            label=label,
            color=color,
            linestyle=linestyle,
        )

    def drawScatter(pos: Vector3, label: str, s: int, color: str) -> None:
        legendElements.append(
            mpl.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=label,
                markerfacecolor=color,
                markersize=10,
            )
        )
        axis.scatter(*pos, color=color, s=s, label=label)

    typeTrajMissile: NDArray[npy.bool_] = npy.array(
        [checkCovered(t) for t in tIterator]
    )
    colorTrajMissile: NDArray[npy.str_] = npy.where(typeTrajMissile, "yellow", "red")

    pointsTrajMissile = trajMissile.reshape(-1, 1, 3)
    segmentsTrajMissile = npy.concatenate(
        [pointsTrajMissile[:-1], pointsTrajMissile[1:]], axis=1
    )
    axis.add_collection(
        Line3DCollection(
            segmentsTrajMissile, colors=colorTrajMissile[:-1], linewidths=2
        )
    )
    drawTrajectory(trajFY1, "无人机FY1轨迹", "blue", "--")
    drawTrajectory(trajDecoy, "烟幕干扰弹轨迹", "darkgreen", "dotted")
    drawTrajectory(trajSmokeSink, "烟幕下沉轨迹", "orange")
    drawScatter(posMissile, color="red", s=50, label="导弹发射点")
    drawScatter(posRealTarget, color="black", s=50, label="真实目标")
    drawScatter(posDetonate, color="orange", s=50, label="烟幕弹爆炸点")
    drawScatter(posRelease, color="brown", s=50, label="烟幕弹投放点")

    u, v = npy.linspace(0, 2 * npy.pi, 30), npy.linspace(0, npy.pi, 30)
    for center in trajSmokeSink[::10]:
        x = center[0] + rCloud * npy.outer(npy.cos(u), npy.sin(v))
        y = center[1] + rCloud * npy.outer(npy.sin(u), npy.sin(v))
        z = center[2] + rCloud * npy.outer(npy.ones(npy.size(u)), npy.cos(v))
        axis.plot_surface(x, y, z, color="gray", alpha=0.1, linewidth=0)

    axis.set_xlabel("X 方向 (米)")
    # axis.set_ylabel("Y 方向 (米)")
    axis.yaxis.set_ticklabels([])  # 隐藏Y轴的刻度值标注
    axis.yaxis.set_ticks([])  # 隐藏Y轴的刻度线
    axis.set_zlabel("Z 方向 (米)")
    axis.set_title("导弹与烟幕干扰弹三维轨迹示意图")
    axis.legend(handles=legendElements, loc="best")

    lim = (
        (17100, 17700),
        (0, 50),
        (1650, 1850),
    )
    axis.set_xlim(lim[0])
    axis.set_ylim(lim[1])
    axis.set_zlim(lim[2])
    axis.set_box_aspect((npy.ptp(lim[0]), npy.ptp(lim[1]), npy.ptp(lim[2])))
    axis.view_init(elev=0, azim=-90)  # 设置视角为面朝XOZ平面

    # 找到第一个 checkCovered(t) == True 的点
    first_covered_index = npy.argmax(typeTrajMissile)
    first_covered_point = trajMissile[first_covered_index]

    # 烟雾爆炸时圆球的顶点
    sphere_top = posDetonate + npy.array([0, 0, rCloud])

    # 绘制线段
    axis.plot(
        [first_covered_point[0], sphere_top[0]],
        [first_covered_point[1], sphere_top[1]],
        [first_covered_point[2] + 1, sphere_top[2]],
        color="purple",
        linewidth=1,
        label="连接线段",
        zorder=5,
        alpha=0.5,
    )

    mpl.show()


# drawPathImage()
