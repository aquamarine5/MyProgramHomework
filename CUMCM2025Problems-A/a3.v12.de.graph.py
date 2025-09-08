import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm
import matplotlib.pyplot as plt

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
DT = 0.01
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
        isCovered = True
        for point in checkpoints:
            isBlocked = False
            for i in range(3):
                if tDetonateList[i] <= instant <= tDetonateList[i] + tCloud:
                    posCloudInstant = getCloudPosition(
                        instant, posDetonateList[i], tDetonateList[i]
                    )
                    if checkLineIntersectSphere(
                        posMissileInstant, point, posCloudInstant, rCloud
                    ):
                        isBlocked = True
                        break
            if not isBlocked:
                isCovered = False
                break
        isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


@numba.njit()
def calculateSingleCloudTime(
    theta: float,
    speedFY: float,
    tRelease1: float,
    tDelay1: float,
) -> float:
    tDetonate = tRelease1 + tDelay1
    directionFY1: Vector3 = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    posFY1Release = posFY1 + speedFY * tRelease1 * directionFY1
    posDetonate = (
        posFY1Release
        + tDelay1 * speedFY * directionFY1
        - 0.5 * G * tDelay1**2 * npy.array([0.0, 0.0, 1.0])
    )

    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        posMissileInstant = getMissilePosition(instant)
        checkpoints = calculateCheckpoints(instant)
        isCovered = True
        for point in checkpoints:
            isBlocked = False
            if tDetonate <= instant <= tDetonate + tCloud:
                posCloudInstant = getCloudPosition(instant, posDetonate, tDetonate)
                if checkLineIntersectSphere(
                    posMissileInstant, point, posCloudInstant, rCloud
                ):
                    isBlocked = True
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


from scipy.optimize import differential_evolution

lb = [0, 70, 0, 0.1, 1, 0.1, 1, 0.1]
ub = [0.5, 140, 5, 3, 10, 3, 20, 3]
bounds = list(zip(lb, ub))

max_iterations = 500

# Set up the progress bar
pbar = tqdm(total=max_iterations, desc="Optimizing")

convergence_history = []


def callback(xk, convergence):
    t = -objectiveCalculateMultipleCloudTime(xk)
    convergence_history.append(t)
    pbar.set_postfix({"t": t})
    pbar.update(1)


result = differential_evolution(
    objectiveCalculateMultipleCloudTime,
    bounds,
    popsize=50,
    maxiter=max_iterations,
    updating="immediate",
    disp=False,
    polish=True,
    callback=callback,
    tol=DT / 10,
)

pbar.close()

print("Best parameters found:", result.x)
print("Maximum masked time:", -result.fun)

plt.figure(figsize=(10, 6))
plt.plot(range(len(convergence_history)), convergence_history)
plt.xlabel("Iteration")
plt.ylabel("Masked Time (s)")
plt.title("Differential Evolution Convergence")
plt.grid(True)
plt.show()


def drawMultipleCloudPathImage(params):
    """
    根据优化后的参数绘制三维轨迹图。
    """
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Line3DCollection

    theta, speedFY, tRelease1, tDelay1, tSpan12, tDelay2, tSpan13, tDelay3 = params

    # --- 复用计算逻辑 ---
    tReleaseList = npy.array([tRelease1, tRelease1 + tSpan12, tRelease1 + tSpan13])
    tDelayList = npy.array([tDelay1, tDelay2, tDelay3])
    tDetonateList = tReleaseList + tDelayList
    directionFY = npy.array([npy.cos(theta), npy.sin(theta), 0.0])

    posFYReleaseList = npy.zeros((3, 3))
    posDetonateList = npy.zeros((3, 3))
    for i in range(3):
        posFYReleaseList[i, :] = posFY1 + speedFY * tReleaseList[i] * directionFY
        posDetonateList[i, :] = (
            posFYReleaseList[i, :]
            + tDelayList[i] * speedFY * directionFY
            - 0.5 * G * tDelayList[i] ** 2 * npy.array([0.0, 0.0, 1.0])
        )

    # --- 定义检查遮蔽的函数 ---
    @numba.jit(nopython=True)
    def checkCovered(t: float) -> bool:
        posMissileInstant = getMissilePosition(t)
        # 使用numba.typed.List替代普通列表
        checkpoints_list = []
        points_cylinder = calculateIntersection(posMissileInstant)
        for p in points_cylinder:
            checkpoints_list.append(p)
        points_perp = calculatePerpendicularIntersection(posMissileInstant)
        for p in points_perp:
            checkpoints_list.append(p)

        isCovered = True
        for point in checkpoints_list:
            isBlocked = False
            for i in range(3):
                if tDetonateList[i] <= t <= tDetonateList[i] + tCloud:
                    posCloudInstant = getCloudPosition(
                        t, posDetonateList[i], tDetonateList[i]
                    )
                    if (
                        distancePoint2Line(posMissileInstant, point, posCloudInstant)
                        <= rCloud
                    ):
                        isBlocked = True
                        break
            if not isBlocked:
                isCovered = False
                break
        return isCovered

    # --- 绘图设置 ---
    fig = plt.figure(figsize=(16, 12))
    axis = fig.add_subplot(111, projection="3d")
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    DRAW_DT = 0.1
    tMax = 20000.0 / speedMissile
    tIterator = npy.arange(0, tMax, DRAW_DT)

    # --- 轨迹计算 ---
    trajMissile = npy.array([getMissilePosition(t) for t in tIterator])
    max_t_release = npy.max(tReleaseList)
    trajFY = npy.array(
        [
            posFY1 + speedFY * t * directionFY
            for t in npy.arange(0, max_t_release + 1, DRAW_DT)
        ]
    )

    # --- 绘制导弹轨迹（分段着色） ---
    typeTrajMissile = npy.array(
        [
            checkCovered(t)
            for t in tqdm(tIterator, desc="Calculating missile coverage for plot")
        ]
    )
    colorTrajMissile = npy.where(typeTrajMissile, "black", "red")
    pointsTrajMissile = trajMissile.reshape(-1, 1, 3)
    segmentsTrajMissile = npy.concatenate(
        [pointsTrajMissile[:-1], pointsTrajMissile[1:]], axis=1
    )
    axis.add_collection(
        Line3DCollection(
            segmentsTrajMissile, colors=colorTrajMissile[:-1], linewidths=2
        )
    )

    # --- 绘制无人机、干扰弹、烟雾轨迹 ---
    axis.plot(
        trajFY[:, 0],
        trajFY[:, 1],
        trajFY[:, 2],
        color="blue",
        linestyle="--",
        label="无人机轨迹",
    )

    for i in range(3):
        # 干扰弹轨迹
        tDecoyIterator = npy.arange(tReleaseList[i], tDetonateList[i], DRAW_DT)
        trajDecoy = npy.array(
            [
                posFYReleaseList[i]
                + speedFY * (t - tReleaseList[i]) * directionFY
                - 0.5 * G * (t - tReleaseList[i]) ** 2 * npy.array([0.0, 0.0, 1.0])
                for t in tDecoyIterator
            ]
        )
        axis.plot(
            trajDecoy[:, 0],
            trajDecoy[:, 1],
            trajDecoy[:, 2],
            color="darkgreen",
            linestyle="dotted",
            label=f"干扰弹{i+1}轨迹" if i == 0 else "",
        )

        # 烟雾下沉轨迹
        trajSmokeSink = npy.array(
            [
                getCloudPosition(t, posDetonateList[i], tDetonateList[i])
                for t in npy.arange(
                    tDetonateList[i], tDetonateList[i] + tCloud, DRAW_DT
                )
            ]
        )
        axis.plot(
            trajSmokeSink[:, 0],
            trajSmokeSink[:, 1],
            trajSmokeSink[:, 2],
            color="orange",
            label=f"烟雾{i+1}下沉轨迹" if i == 0 else "",
        )

        # 烟雾球
        u, v = npy.linspace(0, 2 * npy.pi, 30), npy.linspace(0, npy.pi, 30)
        for center in trajSmokeSink[::15]:  # 每隔一段距离画一个球
            x = center[0] + rCloud * npy.outer(npy.cos(u), npy.sin(v))
            y = center[1] + rCloud * npy.outer(npy.sin(u), npy.sin(v))
            z = center[2] + rCloud * npy.outer(npy.ones(npy.size(u)), npy.cos(v))
            axis.plot_surface(x, y, z, color="gray", alpha=0.05, linewidth=0)

        # 标注点
        axis.scatter(
            *posFYReleaseList[i],
            color="brown",
            s=50,
            label=f"投放点{i+1}" if i == 0 else "",
        )
        axis.scatter(
            *posDetonateList[i],
            color="purple",
            s=50,
            label=f"爆炸点{i+1}" if i == 0 else "",
        )

    # --- 绘制其他静态点 ---
    axis.scatter(*posMissile, color="red", s=50, label="导弹发射点")
    axis.scatter(*posRealTarget, color="black", s=50, label="真实目标")

    # --- 图例和标签 ---
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="gray", alpha=0.3, label="烟幕云覆盖区域"),
        plt.Line2D([0], [0], color="red", lw=2, label="导弹轨迹(未遮蔽)"),
        plt.Line2D([0], [0], color="black", lw=2, label="导弹轨迹(被遮蔽)"),
        plt.Line2D([0], [0], color="blue", lw=2, linestyle="--", label="无人机轨迹"),
        plt.Line2D(
            [0], [0], color="darkgreen", lw=2, linestyle="dotted", label="干扰弹轨迹"
        ),
        plt.Line2D([0], [0], color="orange", lw=2, label="烟雾下沉轨迹"),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="投放点",
            markerfacecolor="brown",
            markersize=10,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="爆炸点",
            markerfacecolor="purple",
            markersize=10,
        ),
    ]
    axis.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1, 1))

    axis.set_xlabel("X (m)")
    axis.set_ylabel("Y (m)")
    axis.set_zlabel("Z (m)")
    axis.set_title("多烟幕弹协同遮蔽三维轨迹示意图")

    # --- 调整视角和范围 ---
    x_mid = npy.mean(posDetonateList[:, 0])
    y_mid = npy.mean(posDetonateList[:, 1])
    z_mid = npy.mean(posDetonateList[:, 2])
    span = 800
    axis.set_xlim(x_mid - span, x_mid + span)
    axis.set_ylim(y_mid - span, y_mid + span)
    axis.set_zlim(z_mid - span, z_mid + span)

    axis.set_box_aspect((1, 1, 1))  # 等比例显示
    plt.show()


drawMultipleCloudPathImage(result.x)

# drawMultipleCloudPathImage(result.x)


def save_results_to_csv(params: List[float], result_fun: float):
    """
    将差分进化优化结果保存到CSV文件中。
    """
    # 1. 导入所需模块
    import datetime
    import csv

    # 2. 提取最优参数和结果
    theta, speedFY, tRelease1, tDelay1, tSpan12, tDelay2, tSpan13, tDelay3 = params
    effective_time = -result_fun
    theta_deg = npy.rad2deg(theta)  # 将弧度转换为度

    # 3. 根据最优参数重新计算所需信息
    directionFY: Vector3 = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    tReleaseList = npy.array([tRelease1, tRelease1 + tSpan12, tRelease1 + tSpan13])
    tDelayList = npy.array([tDelay1, tDelay2, tDelay3])

    posFYReleaseList = npy.zeros((3, 3))
    posDetonateList = npy.zeros((3, 3))
    for i in range(3):
        posFYReleaseList[i, :] = posFY1 + speedFY * tReleaseList[i] * directionFY
        posDetonateList[i, :] = (
            posFYReleaseList[i, :]
            + tDelayList[i] * speedFY * directionFY
            - 0.5 * G * tDelayList[i] ** 2 * npy.array([0.0, 0.0, 1.0])
        )

    # 4. 准备CSV文件名
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"A题/result.a3.v12-{effective_time:.4f}-{timestamp}.csv"

    # 5. 准备表头和数据行
    header = [
        "无人机运动方向 (deg)",
        "无人机运动速度 (m/s)",
        "烟幕干扰弹编号",
        "烟幕干扰弹投放点的x坐标 (m)",
        "烟幕干扰弹投放点的y坐标 (m)",
        "烟幕干扰弹投放点的z坐标 (m)",
        "烟幕干扰弹起爆点的x坐标 (m)",
        "烟幕干扰弹起爆点的y坐标 (m)",
        "烟幕干扰弹起爆点的z坐标 (m)",
        "总有效干扰时长 (s)",
    ]
    rows = []
    for i in range(3):
        row = [
            f"{theta_deg:.4f}",
            f"{speedFY:.4f}",
            f"弹{i+1}",
            f"{posFYReleaseList[i, 0]:.4f}",
            f"{posFYReleaseList[i, 1]:.4f}",
            f"{posFYReleaseList[i, 2]:.4f}",
            f"{posDetonateList[i, 0]:.4f}",
            f"{posDetonateList[i, 1]:.4f}",
            f"{posDetonateList[i, 2]:.4f}",
            f"{calculateSingleCloudTime(theta,speedFY,tReleaseList[i],tDelayList[i])}",  # 总时长只在第一行显示
        ]
        rows.append(row)

    # 6. 写入CSV文件
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"\n结果已成功保存到文件: {filename}")
    except Exception as e:
        print(f"\n保存文件时出错: {e}")


# 在脚本的最后调用函数以保存结果
save_results_to_csv(result.x, result.fun)
