import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm

Vector3 = NDArray[npy.float64]
Trajectory = List[Vector3]  # or NDArray[npy.float64]

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
posFakeTarget: Vector3 = posMissileTarget
from numba.typed import List as NumbaList
from numba.experimental import jitclass

speedFYMin = 70.0
speedFYMax = 140.0
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


@numba.njit()
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


@numba.njit()
def checkSmokeBetween(
    posMissile: Vector3, posCloud: Vector3, posCheckpoint: Vector3
) -> bool:
    return npy.dot(posCloud - posMissile, posCheckpoint - posMissile) > 0


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


@numba.njit()
def checkCovered(t: float, tDetonate: float, posDetonate: Vector3) -> bool:
    if t < tDetonate or t > tDetonate + tCloud:
        return False
    posNowMissile = getMissilePosition(t)
    checkpoints = calculateCheckpoints(t)
    posNowCloud = getCloudPosition(t, posDetonate, tDetonate)
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


DT = 0.001


@numba.njit()
def calculateCoverTimeV2(
    thetaFY1: float, vFY1: float, tRelease: float, tDelay: float
) -> List[Tuple[float, float]]:
    tToMissile = posFakeTarget[0] - posMissile[0] / vMissile[0]
    tDetonate = tRelease + tDelay
    tStart = 0
    tEnd = min(tCloud, tToMissile - tDetonate)
    if tEnd <= 0:
        return [(0.0, 0.0)]
    intervals = []
    isInCover = False
    posRelease: Vector3 = posFY1 + vFY1 * tRelease * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate: Vector3 = posRelease + vFY1 * tDelay * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
    numSteps = int((tEnd - tStart) / DT)
    for i in range(numSteps + 1):
        currentTime = tStart + i * DT
        tMissile = tDetonate + currentTime
        posMissileNow = getMissilePosition(tMissile)
        posCloudNow = getCloudPosition(currentTime, posDetonate, tDetonate)
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


def objectiveCalculateCoverTimeV2(params: NDArray[npy.float64]) -> float:
    thetaFY1, vFY1, tRelease, tDelay = params
    intervals = calculateCoverTime(thetaFY1, vFY1, tRelease, tDelay)
    totalCoverTime = 0.0
    for start, end in intervals:
        totalCoverTime += end - start
    return -totalCoverTime


@numba.njit()
def calculateCoverTime(
    thetaFY1: float, vFY1: float, tRelease: float, tDelay: float
) -> List[Tuple[float, float]]:
    posRelease: Vector3 = posFY1 + vFY1 * tRelease * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate: Vector3 = posRelease + vFY1 * tDelay * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
    tDetonate = tRelease + tDelay
    iterator = npy.arange(0, tDetonate + tCloud + 1, DT)

    intervals = []
    is_covered = False
    start_cover_time = 0.0

    for t in iterator:
        currently_covered = checkCovered(t, tDetonate, posDetonate)
        if currently_covered and not is_covered:
            is_covered = True
            start_cover_time = t
        elif not currently_covered and is_covered:
            is_covered = False
            intervals.append((start_cover_time, t))

    if is_covered:
        intervals.append((start_cover_time, iterator[-1]))

    return intervals


from scipy.optimize import basinhopping, Bounds


@numba.njit()
def objective_function_wrapper(params: NDArray[npy.float64]) -> float:
    theta, v, tRelease, tDelay = params
    # 我们想要最大化 tCover，所以我们最小化 -tCover
    res = calculateCoverTime(theta, v, tRelease, tDelay)
    return -res.tCover


if __name__ == "__main__":
    # theta, vFY1, tRelease, tDelay 参数边界
    bounds = Bounds(
        [npy.deg2rad(175), speedFYMin, 0, 0], [npy.deg2rad(185), speedFYMax, 5, 5]
    )

    # 初始猜测值 (在边界范围内)
    x0 = npy.array([npy.deg2rad(180), 70, 1, 2])

    n_iterations = 5000
    pbar = tqdm(total=n_iterations, desc="Progress")

    # 使用一个可变对象（如列表）来存储跨回调函数的最佳值
    best_f_value = [float("inf")]

    # 定义回调函数来更新进度条
    def progress_callback(x, f, accept):
        # f 是 -totalCoverTime，我们想找到最小的 f
        if f < best_f_value[0]:
            best_f_value[0] = f
        pbar.update(1)
        # -best_f_value[0] 得到的就是最大的 totalCoverTime
        pbar.set_postfix(best_tCover=f"{-best_f_value[0]:.4f}", refresh=True)

    print("正在使用 basinhopping 算法进行全局优化...")
    # 调用 basinhopping
    # niter: 全局优化迭代次数
    # T: 退火温度
    # stepsize: 步长
    minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}
    result: OptimizeResult = basinhopping(
        objectiveCalculateCoverTimeV2,
        x0,
        minimizer_kwargs=minimizer_kwargs,
        niter=n_iterations,
        T=5.0,
        stepsize=0.02,
        callback=progress_callback,
    )
    pbar.close()

    print("优化完成！")

    # 提取最佳参数
    best_params = result.x
    best_tCover = -result.fun

    theta_opt, v_opt, tRelease_opt, tDelay_opt = best_params

    # 使用最优参数重新计算以获取完整的 CoverResult 对象
    best_res = calculateCoverTime(theta_opt, v_opt, tRelease_opt, tDelay_opt)
    print(f"最佳参数:")
    print(f"发射角度: {npy.rad2deg(theta_opt):.2f}°")
    print(f"发射速度: {v_opt:.2f} m/s")
    print(f"释放时间: {tRelease_opt:.2f} s")
    print(f"延迟时间: {tDelay_opt:.2f} s")
    print(f"最大覆盖时间: {best_tCover:.2f} s")
    print(f"覆盖时间区间: {best_res}")
