import numba
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from tqdm import tqdm

Vector3 = NDArray[npy.float64]
Trajectory = List[Vector3]

posMissile: Vector3 = npy.array([20000.0, 0.0, 2000.0])
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])
directionMissile: Vector3 = (posMissileTarget - posMissile) / npy.linalg.norm(
    posMissileTarget - posMissile
)
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
rRealTarget = 7
hRealTarget = 10
posFY1: Vector3 = npy.array([17800.0, 0.0, 1800.0])

from numba.typed import List as NumbaList
from numba.experimental import jitclass

G = 9.8
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

spec = [
    ("tCover", numba.float64),
    ("theta", numba.float64),
    ("v", numba.float64),
    ("tRelease", numba.float64),
    ("tDelay", numba.float64),
    ("tDetonate", numba.float64),
    ("posDetonate", numba.float64[:]),
]


@jitclass(spec)
class CoverResult:
    def __init__(self, tCover, theta, v, tRelease, tDelay, tDetonate, posDetonate):
        self.tCover = tCover
        self.theta = theta
        self.v = v
        self.tRelease = tRelease
        self.tDelay = tDelay
        self.tDetonate = tDetonate
        self.posDetonate = posDetonate


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
    return result + [
        npy.array([cx, cy, cz]),
        npy.array([dx, dy, dz]),
        npy.array([gx, gy, gz]),
        npy.array([hx, hy, hz]),
    ]


@numba.jit()
def calculateCheckpoints(t: float) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t)

    points = []

    points_cylinder = calculate_intersection_with_cylinder(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    points_perp = calculate_perpendicular_plane_intersection(posNowMissile)
    for p in points_perp:
        points.append(p)

    return points


@numba.jit()
def checkCovered(t: float, tDetonate: float, posDetonate: Vector3) -> bool:
    if t < tDetonate or t > tDetonate + tCloud:
        return False
    posNowMissile = getMissilePosition(t)
    checkpoints = calculateCheckpoints(t)

    for checkpoint in checkpoints:
        d = distancePoint2Line(
            posNowMissile, checkpoint, getCloudPosition(t, posDetonate, tDetonate)
        )
        if d > rCloud:
            return False
    return True


DT = 0.001


@numba.jit()
def calculateCoverTime(
    thetaFY1: float, vFY1: float, tRelease: float, tDelay: float
) -> CoverResult:
    posRelease: Vector3 = posFY1 + vFY1 * tRelease * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate: Vector3 = posRelease + vFY1 * tDelay * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
    tDetonate = tRelease + tDelay
    iterator = npy.arange(0, tDetonate + tCloud + 1, DT)

    tTotalCovered = 0.0
    isCovered = False
    tStartCover = 0.0

    for time in iterator:
        isCoveredNow = checkCovered(time, tDetonate, posDetonate)
        if isCoveredNow and not isCovered:
            isCovered = True
            tStartCover = time
        elif not isCoveredNow and isCovered:
            isCovered = False
            tTotalCovered += time - tStartCover

    if isCovered:
        tTotalCovered += iterator[-1] - tStartCover

    return CoverResult(
        tTotalCovered, thetaFY1, vFY1, tRelease, tDelay, tDetonate, posDetonate
    )


if __name__ == "__main__":
    N_ITERATIONS = 2000  # 总迭代次数
    NEIGHBORHOOD_SIZE = 10  # 每个邻域的大小
    INITIAL_TEMP = 10.0  # 模拟退火初始温度
    COOLING_RATE = 0.995  # 冷却率

    thetaIterator = (npy.deg2rad(165), npy.deg2rad(195))
    vIterator = (70.0, 140.0)
    tReleaseIterator = (0.0, 60.0)
    tDelayIterator = (0.0, 60.0)

    initialTheta = npy.random.uniform(*thetaIterator)
    initialV = npy.random.uniform(*vIterator)
    initialTRelease = npy.random.uniform(*tReleaseIterator)
    initialTDelay = npy.random.uniform(*tDelayIterator)

    currentSolution = calculateCoverTime(
        initialTheta, initialV, initialTRelease, initialTDelay
    )
    bestSolution = currentSolution

    history = [currentSolution]
    temp = INITIAL_TEMP

    with tqdm(total=N_ITERATIONS, desc="LNS Progress") as pbar:
        for i in range(N_ITERATIONS):
            candidates = []
            for _ in range(NEIGHBORHOOD_SIZE):
                numParamsChange = npy.random.randint(1, 5)
                paramsChange = npy.random.choice(
                    ["theta", "v", "tRelease", "tDelay"],
                    numParamsChange,
                    replace=False,
                )

                newTheta, newV, newTRelease, newTDelay = (
                    currentSolution.theta,
                    currentSolution.v,
                    currentSolution.tRelease,
                    currentSolution.tDelay,
                )

                if "theta" in paramsChange:
                    newTheta = npy.random.uniform(*thetaIterator)
                if "v" in paramsChange:
                    newV = npy.random.uniform(*vIterator)
                if "tRelease" in paramsChange:
                    newTRelease = npy.random.uniform(*tReleaseIterator)
                if "tDelay" in paramsChange:
                    newTDelay = npy.random.uniform(*tDelayIterator)

                candidates.append(
                    calculateCoverTime(newTheta, newV, newTRelease, newTDelay)
                )
            neighborhoodBest = max(candidates, key=lambda x: x.tCover)
            deltaE = neighborhoodBest.tCover - currentSolution.tCover

            if deltaE > 0:
                currentSolution = neighborhoodBest
                if currentSolution.tCover > bestSolution.tCover:
                    bestSolution = currentSolution
            elif npy.exp(deltaE / temp) > npy.random.rand():
                currentSolution = neighborhoodBest

            history.append(currentSolution)
            temp *= COOLING_RATE
            pbar.update(1)
            pbar.set_postfix(
                {
                    "Best tCover": f"{bestSolution.tCover:.4f}",
                }
            )

    print("\nLNS search finished.")
    print("\n最佳结果:")
    print(f"覆盖时间: {bestSolution.tCover:.4f} 秒")
    print(f"发射角度: {npy.rad2deg(bestSolution.theta):.2f}°")
    print(f"发射速度: {bestSolution.v:.2f} m/s")
    print(f"释放时间: {bestSolution.tRelease:.2f} s")
    print(f"延迟时间: {bestSolution.tDelay:.2f} s")
    print(f"引爆时间: {bestSolution.tDetonate:.2f} s")
    print(
        f"引爆位置: ({bestSolution.posDetonate[0]:.2f}, {bestSolution.posDetonate[1]:.2f}, {bestSolution.posDetonate[2]:.2f})"
    )
    import matplotlib.pyplot as pyplot
    import pandas as pd

    df = pd.DataFrame(
        {
            "theta_deg": [npy.rad2deg(h.theta) for h in history],
            "v_ms": [h.v for h in history],
            "tRelease_s": [h.tRelease for h in history],
            "tDelay_s": [h.tDelay for h in history],
            "tCover_s": [h.tCover for h in history],
        }
    )
    csv_filename = "a2_lns_results.csv"
    df.to_csv(csv_filename, index_label="Iteration", float_format="%.5f")
    print(f"\n所有迭代数据已保存到 {csv_filename}")

    tCovers_history = df["tCover_s"].tolist()
    best_tCovers_history = [
        max(tCovers_history[: i + 1]) for i in range(len(tCovers_history))
    ]
    convergence_df = pd.DataFrame(
        {"current_tCover_s": tCovers_history, "best_tCover_s": best_tCovers_history}
    )
    convergence_csv_filename = "a2_lns_convergence.csv"
    convergence_df.to_csv(
        convergence_csv_filename, index_label="Iteration", float_format="%.5f"
    )
    print(f"收敛过程数据已保存到 {convergence_csv_filename}")
    pyplot.rcParams["font.sans-serif"] = ["SimHei"]
    pyplot.rcParams["axes.unicode_minus"] = False
    pyplot.figure(figsize=(10, 6))
    tCovers_history = df["tCover_s"].tolist()
    best_tCovers_history = [
        max(tCovers_history[: i + 1]) for i in range(len(tCovers_history))
    ]
    pyplot.plot(tCovers_history, label="当前覆盖时间")
    pyplot.plot(best_tCovers_history, label="最佳覆盖时间", color="r", linestyle="--")
    pyplot.xlabel("迭代次数")
    pyplot.ylabel("覆盖时间 (s)")
    pyplot.title("收敛过程")
    pyplot.legend()
    pyplot.grid(True)
    pyplot.tight_layout()
    pyplot.show()

    pyplot.figure(figsize=(10, 6))
    sc2 = pyplot.scatter(
        df["theta_deg"], df["tCover_s"], c=df["tCover_s"], cmap="viridis", alpha=0.6
    )
    pyplot.colorbar(sc2, label="覆盖时间 (s)")
    pyplot.xlabel("发射角度 (°)")
    pyplot.ylabel("覆盖时间 (s)")
    pyplot.title("角度 vs. 覆盖时间")
    pyplot.grid(True)
    pyplot.tight_layout()
    pyplot.show()

    pyplot.figure(figsize=(10, 6))
    sc3 = pyplot.scatter(
        df["v_ms"], df["tCover_s"], c=df["tCover_s"], cmap="viridis", alpha=0.6
    )
    pyplot.colorbar(sc3, label="覆盖时间 (s)")
    pyplot.xlabel("发射速度 (m/s)")
    pyplot.ylabel("覆盖时间 (s)")
    pyplot.title("速度 vs. 覆盖时间")
    pyplot.grid(True)
    pyplot.tight_layout()
    pyplot.show()

    pyplot.figure(figsize=(10, 6))
    sc4 = pyplot.scatter(
        df["tRelease_s"],
        df["tDelay_s"],
        c=df["tCover_s"],
        cmap="viridis",
        s=50,
        alpha=0.7,
    )
    pyplot.colorbar(sc4, label="覆盖时间 (s)")
    pyplot.xlabel("释放时间 (s)")
    pyplot.ylabel("延迟时间 (s)")
    pyplot.title("释放/延迟时间 vs. 覆盖时间")
    pyplot.grid(True)
    pyplot.tight_layout()
    pyplot.show()
