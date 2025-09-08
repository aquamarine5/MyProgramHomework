import numba
from numpy.typing import NDArray
import numpy as npy
import pandas as pds
import matplotlib.pyplot as mpl
from typing import List, Tuple
from tqdm import tqdm

Vector3 = NDArray[npy.float64]
Trajectory = List[Vector3]  # or NDArray[npy.float64]

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
    return [
        npy.array([cx, cy, cz]),
        npy.array([dx, dy, dz]),
        npy.array([gx, gy, gz]),
        npy.array([hx, hy, hz]),
    ]


@numba.jit()
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


DT = 0.01


@numba.jit()
def calculate_total_cover_time_for_3_bombs(
    theta: float,
    v: float,
    t_release1: float,
    t_delay1: float,
    t_release2: float,
    t_delay2: float,
    t_release3: float,
    t_delay3: float,
) -> float:
    # 检查投放时间间隔约束
    if not (t_release2 >= t_release1 + 1.0 and t_release3 >= t_release2 + 1.0):
        return 0.0

    # Numba JIT-compiled functions don't support list of dicts well.
    # Let's use a list of tuples (t_detonate, pos_detonate).
    # Pre-allocate a list of tuples. Numba needs to infer the types.
    bombs = [
        (0.0, npy.array([0.0, 0.0, 0.0])),
        (0.0, npy.array([0.0, 0.0, 0.0])),
        (0.0, npy.array([0.0, 0.0, 0.0])),
    ]
    releases = [t_release1, t_release2, t_release3]
    delays = [t_delay1, t_delay2, t_delay3]

    for i in range(3):
        t_release = releases[i]
        t_delay = delays[i]
        pos_release = posFY1 + v * t_release * npy.array(
            [npy.cos(theta), npy.sin(theta), 0.0]
        )
        t_detonate = t_release + t_delay
        pos_detonate = pos_release.copy()  # Use copy to avoid modifying pos_release
        pos_detonate[2] = pos_release[2] - 0.5 * G * (t_delay**2)
        bombs[i] = (t_detonate, pos_detonate)

    # 确定模拟的时间范围
    max_t_detonate = 0.0
    for b_td, b_pd in bombs:
        if b_td > max_t_detonate:
            max_t_detonate = b_td

    simulation_end_time = max_t_detonate + tCloud + 1.0
    iterator = npy.arange(0, simulation_end_time, DT)

    total_covered_time = 0.0
    is_covered = False
    start_cover_time = 0.0

    for t in iterator:
        currently_covered = False
        for i in range(len(bombs)):
            t_det, pos_det = bombs[i]
            if checkCovered(t, t_det, pos_det):
                currently_covered = True
                break  # 只要有一个云团覆盖，该时刻就有效

        if currently_covered and not is_covered:
            is_covered = True
            start_cover_time = t
        elif not currently_covered and is_covered:
            is_covered = False
            total_covered_time += t - start_cover_time

    if is_covered:
        # 如果在模拟结束时仍然被覆盖
        total_covered_time += iterator[-1] - start_cover_time

    return total_covered_time


if __name__ == "__main__":
    FIND_SCALE = 5  # 减少搜索规模以加快计算速度
    best_t_cover = 0.0
    best_params = {}

    # 定义搜索范围
    theta_range = npy.linspace(npy.deg2rad(175), npy.deg2rad(185), FIND_SCALE)
    v_range = npy.linspace(70, 140, FIND_SCALE)
    t_release_range = npy.linspace(0, 5, FIND_SCALE)  # 扩展释放时间范围
    t_delay_range = npy.linspace(2, 5, FIND_SCALE)

    # 迭代次数巨大，需要简化
    total_iterations = FIND_SCALE**8
    with tqdm(total=total_iterations, desc="Processing Q3", unit="iteration") as pbar:
        for theta in theta_range:
            for v in v_range:
                for tr1 in t_release_range:
                    for td1 in t_delay_range:
                        for tr2 in t_release_range:
                            if tr2 < tr1 + 1.0:
                                pbar.update(FIND_SCALE**4)
                                continue
                            for td2 in t_delay_range:
                                for tr3 in t_release_range:
                                    if tr3 < tr2 + 1.0:
                                        pbar.update(FIND_SCALE**2)
                                        continue
                                    for td3 in t_delay_range:
                                        t_cover = (
                                            calculate_total_cover_time_for_3_bombs(
                                                theta, v, tr1, td1, tr2, td2, tr3, td3
                                            )
                                        )
                                        if t_cover > best_t_cover:
                                            best_t_cover = t_cover
                                            best_params = {
                                                "theta": theta,
                                                "v": v,
                                                "t_release1": tr1,
                                                "t_delay1": td1,
                                                "t_release2": tr2,
                                                "t_delay2": td2,
                                                "t_release3": tr3,
                                                "t_delay3": td3,
                                                "total_cover_time": t_cover,
                                            }
                                        pbar.update(1)

    print("Best parameters found:")
    print(best_params)

    # 保存结果到 result1.xlsx
    if best_params:
        df_data = []
        theta = best_params["theta"]
        v = best_params["v"]
        releases = [
            best_params["t_release1"],
            best_params["t_release2"],
            best_params["t_release3"],
        ]
        delays = [
            best_params["t_delay1"],
            best_params["t_delay2"],
            best_params["t_delay3"],
        ]

        for i in range(3):
            t_release = releases[i]
            t_delay = delays[i]
            pos_release = posFY1 + v * t_release * npy.array(
                [npy.cos(theta), npy.sin(theta), 0.0]
            )
            t_detonate = t_release + t_delay
            pos_detonate = pos_release.copy()
            pos_detonate[2] -= 0.5 * G * (t_delay**2)

            df_data.append(
                {
                    "无人机编号": "FY1",
                    "干扰弹编号": i + 1,
                    "飞行方向（弧度）": theta,
                    "飞行速度（m/s）": v,
                    "投放时间（s）": t_release,
                    "投放点x": pos_release[0],
                    "投放点y": pos_release[1],
                    "投放点z": pos_release[2],
                    "延迟时间（s）": t_delay,
                    "起爆点x": pos_detonate[0],
                    "起爆点y": pos_detonate[1],
                    "起爆点z": pos_detonate[2],
                }
            )

        df = pds.DataFrame(df_data)
        # 确保A题/附件目录存在
        import os

        output_dir = "A题/附件"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "result1.xlsx")
        df.to_excel(output_path, index=False)
        print(f"结果已保存到 {output_path}")
        print(f"最大总遮蔽时间: {best_t_cover} s")
    else:
        print("未能找到有效的投放策略。")
