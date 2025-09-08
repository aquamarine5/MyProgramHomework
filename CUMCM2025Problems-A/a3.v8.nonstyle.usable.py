import sys
from warnings import deprecated
import numba
import numba.types
from numpy.typing import NDArray
import numpy as npy
import numpy as np
from typing import List, Tuple
import pandas as pd
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm

Vector3 = NDArray[npy.float64]
from scipy.optimize import differential_evolution

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
g = 9.8  # 重力加速度
v_M1 = 300  # 导弹速度
R_cloud = 10  # 烟幕半径
v_sink = 3  # 烟幕下沉速度
cloud_lifetime = 20  # 烟幕有效时间
cylinder_radius = 7  # 真实目标圆柱体半径
cylinder_height = 10  # 圆柱体高度

speedFYMin = 70.0
speedFYMax = 140.0
G = 9.8
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0
# 初始位置
r_M1_0 = np.array([20000, 0, 2000])  # 导弹初始
r_FY1_0 = np.array([17800, 0, 1800])  # 无人机初始
O = np.array([0, 0, 0])  # 假目标
T_base = np.array([0, 200, 0])  # 真目标底面圆心

# 导弹方向
e_M1 = (O - r_M1_0) / np.linalg.norm(O - r_M1_0)

# 时间范围
t_start = 0
t_end = 100
dt = 0.1
t_range = np.arange(t_start, t_end + dt, dt)

# ---------------- 辅助函数 ----------------


@deprecated("get1SixDynamicPoints is deprecated, use get6DynamicPoints instead")
def get6DynamicPoints(t):
    """根据推导公式生成6个动点"""
    X = 20000 - (3000 * np.sqrt(101) / 101) * t

    # 上圆 (z=10)
    denom_sqrt_X2_40000 = np.sqrt(X**2 + 40000)
    if denom_sqrt_X2_40000 == 0:
        return np.zeros((6, 3))  # Avoid division by zero

    pu_x = 1400 * X / (200 * denom_sqrt_X2_40000)
    pu_y = 200 - 1400 / denom_sqrt_X2_40000
    P1 = [pu_x, pu_y, 10]

    denom_sqrt_200_X2 = np.sqrt(200**2 + X**2)
    if denom_sqrt_200_X2 == 0:
        return np.zeros((6, 3))  # Avoid division by zero

    lu_x = 1400 / denom_sqrt_200_X2
    lu_y = 7 * X / denom_sqrt_200_X2
    P2 = [lu_x, 200 + lu_y, 10]
    P3 = [-lu_x, 200 - lu_y, 10]

    # 下圆 (z=0)
    pl_x = 1400 * X / (200 * denom_sqrt_200_X2)
    pl_y = 200 - 1400 / denom_sqrt_200_X2
    P4 = [pl_x, pl_y, 0]

    ll_x = 1400 / denom_sqrt_200_X2
    ll_y = 7 * X / denom_sqrt_200_X2
    P5 = [ll_x, 200 + ll_y, 0]
    P6 = [-ll_x, 200 - ll_y, 0]

    return np.array([P1, P2, P3, P4, P5, P6])


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
def calculate_intersection_with_cylinder(
    posMissile: Vector3,
):
    v2directionMissile = posMissile[:2] - posRealTarget[:2]

    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)

    pointsIntersection = []

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]

        pointsIntersection.append([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        pointsIntersection.append([x, y, posRealTarget[2]])  # 底部

    return pointsIntersection


@numba.jit()
def calculate_perpendicular_plane_intersection(
    posMissile: Vector3,
):
    v2directionMissile = posMissile[:2] - posRealTarget[:2]

    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)

    directionPerpendicular = npy.array([-directionMissile[1], directionMissile[0]])

    pointsIntersection = []

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionPerpendicular[0]
        y = posRealTarget[1] + sign * rRealTarget * directionPerpendicular[1]

        pointsIntersection.append([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        pointsIntersection.append([x, y, posRealTarget[2]])  # 底部

    return pointsIntersection


@deprecated("get1SixDynamicPoints is deprecated, use get6DynamicPoints instead")
def get1SixDynamicPoints(t: float) -> List[Vector3]:
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
    result = np.array([])
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
def getSixDynamicPoints(t: float) -> Vector3:
    posNowMissile: Vector3 = getMissilePosition(t)

    # Use a Numba typed list for compatibility
    # points: List[NDArray] = []

    # Manually append items from the first function call
    points_cylinder = calculate_intersection_with_cylinder(posNowMissile)
    # for p in points_cylinder:
    #     points.append(p)

    # Manually append items from the second function call
    points_perp = calculate_perpendicular_plane_intersection(posNowMissile)
    # for p in points_perp:
    #     points.append(p)
    return np.array(
        [
            points_cylinder[0],
            points_cylinder[1],
            points_cylinder[2],
            points_cylinder[3],
            points_perp[0],
            points_perp[1],
            points_perp[2],
            points_perp[3],
        ]
    )


def isLineSegmentIntersectSphere(p1, p2, c, r):
    """判断线段(p1, p2)是否与球体(c, r)相交"""
    p1, p2, c = np.array(p1), np.array(p2), np.array(c)
    d1 = np.linalg.norm(p1 - c)
    d2 = np.linalg.norm(p2 - c)
    if d1 <= r or d2 <= r:
        return True
    v = p2 - p1
    a = np.dot(v, v)
    b = 2 * np.dot(p1 - c, v)
    c2 = np.dot(p1 - c, p1 - c) - r**2
    disc = b**2 - 4 * a * c2
    if disc < 0:
        return False
    sqrt_disc = np.sqrt(disc)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)
    return (0 <= t1 <= 1) or (0 <= t2 <= 1)


def calculate_multiple_flares_shielding_time_incremental(
    theta,
    r_M1_0,
    e_M1,
    v_M1,
    r_FY1_0,
    g,
    R_cloud,
    v_sink,
    cloud_lifetime,
    T_base,
    R,
    H,
    t_range,
    dt,
):
    print(
        theta,
        r_M1_0,
        e_M1,
        v_M1,
        r_FY1_0,
        g,
        R_cloud,
        v_sink,
        cloud_lifetime,
        T_base,
        R,
        H,
        t_range,
        dt,
    )
    """计算多枚烟幕弹的总有效遮蔽时间（适应优化器）"""
    angle, speed = theta[0], theta[1]
    t_release = np.zeros(3)
    t_delay = np.zeros(3)

    t_release[0] = theta[2]
    t_delay[0] = theta[3]
    t_release[1] = t_release[0] + theta[4]
    t_delay[1] = theta[5]
    t_release[2] = t_release[1] + theta[6]
    t_delay[2] = theta[7]

    t_explosion = t_release + t_delay
    e_FY1 = np.array([np.cos(angle), np.sin(angle), 0])

    r_FY1_release = np.zeros((3, 3))
    r_S_explosion = np.zeros((3, 3))
    for i in range(3):
        r_FY1_release[i, :] = r_FY1_0 + speed * t_release[i] * e_FY1
        r_S_explosion[i, :] = (
            r_FY1_release[i, :]
            + t_delay[i] * speed * e_FY1
            - 0.5 * g * t_delay[i] ** 2 * np.array([0, 0, 1])
        )

    is_eff = np.zeros(len(t_range))
    for it, t in enumerate(t_range):
        rM = r_M1_0 + v_M1 * t * e_M1
        moving_points = getSixDynamicPoints(t)
        covered = True
        for k in range(moving_points.shape[0]):
            pt = moving_points[k, :]
            blocked = False
            for j in range(3):
                if t_explosion[j] <= t <= t_explosion[j] + cloud_lifetime:
                    rC = r_S_explosion[j, :] - v_sink * (t - t_explosion[j]) * np.array(
                        [0, 0, 1]
                    )
                    if isLineSegmentIntersectSphere(rM, pt, rC, R_cloud):
                        blocked = True
                        break
            if not blocked:
                covered = False
                break
        is_eff[it] = 1 if covered else 0

    effective_time = np.sum(is_eff) * dt
    return -effective_time  # 优化器默认最小化，因此返回负值


def calculate_single_flare_time(
    theta,
    r_M1_0,
    e_M1,
    v_M1,
    r_FY1_0,
    g,
    R_cloud,
    v_sink,
    cloud_lifetime,
    T_base,
    R,
    H,
    t_range,
    dt,
):
    """计算单枚烟幕弹的遮蔽时长和区间"""
    angle, speed, t_release, t_delay = theta
    t_explosion = t_release + t_delay
    e_FY1 = np.array([np.cos(angle), np.sin(angle), 0])
    r_FY1_release = r_FY1_0 + speed * t_release * e_FY1
    r_S_explosion = (
        r_FY1_release
        + t_delay * speed * e_FY1
        - 0.5 * g * t_delay**2 * np.array([0, 0, 1])
    )

    is_eff = np.zeros(len(t_range))
    for it, t in enumerate(t_range):
        if t_explosion <= t <= t_explosion + cloud_lifetime:
            rM = r_M1_0 + v_M1 * t * e_M1
            rC = r_S_explosion - v_sink * (t - t_explosion) * np.array([0, 0, 1])
            pts = getSixDynamicPoints(t)
            covered = True
            for k in range(pts.shape[0]):
                if not isLineSegmentIntersectSphere(rM, pts[k, :], rC, R_cloud):
                    covered = False
                    break
            is_eff[it] = 1 if covered else 0

    eff_time = np.sum(is_eff) * dt

    # 提取区间
    intervals = []
    idx = np.where(is_eff == 1)[0]
    if len(idx) > 0:
        start_idx = idx[0]
        for i in range(1, len(idx)):
            if idx[i] != idx[i - 1] + 1:
                intervals.append((t_range[start_idx], t_range[idx[i - 1]]))
                start_idx = idx[i]
        intervals.append((t_range[start_idx], t_range[idx[-1]]))

    return eff_time, intervals


if __name__ == "__main__":
    # 变量边界
    bounds = [
        (0, 0.5),
        (70, 140),
        (0, 5),
        (0.1, 3),
        (1, 10),
        (0.1, 3),
        (1, 20),
        (0.1, 3),
    ]

    # 优化
    print("开始优化...")
    result = differential_evolution(
        calculate_multiple_flares_shielding_time_incremental,
        bounds,
        args=(
            r_M1_0,
            e_M1,
            v_M1,
            r_FY1_0,
            g,
            R_cloud,
            v_sink,
            cloud_lifetime,
            T_base,
            cylinder_radius,
            cylinder_height,
            t_range,
            dt,
        ),
        popsize=15,  # 类似于'PopulationSize'
        maxiter=50,  # 类似于'MaxGenerations'
        updating="immediate",
        disp=True,
        polish=True,
    )

    optimal_params = result.x
    max_shielding_time = -result.fun

    print("\n优化完成！")
    print("最优参数:", optimal_params)
    print(f"总有效遮蔽时间: {max_shielding_time:.4f} 秒")

    angle, speed = optimal_params[0], optimal_params[1]
    t_release = np.zeros(3)
    t_delay = np.zeros(3)

    t_release[0] = optimal_params[2]
    t_delay[0] = optimal_params[3]
    t_release[1] = t_release[0] + optimal_params[4]
    t_delay[1] = optimal_params[5]
    t_release[2] = t_release[1] + optimal_params[6]
    t_delay[2] = optimal_params[7]

    t_explosion = t_release + t_delay
    e_FY1 = np.array([np.cos(angle), np.sin(angle), 0])

    release_pos = np.zeros((3, 3))
    explosion_pos = np.zeros((3, 3))
    for i in range(3):
        release_pos[i, :] = r_FY1_0 + speed * t_release[i] * e_FY1
        tau = t_delay[i]
        explosion_pos[i, :] = (
            release_pos[i, :]
            + tau * speed * e_FY1
            - 0.5 * g * tau**2 * np.array([0, 0, 1])
        )

    # 单独遮蔽时长 & 区间
    single_times = []
    intervals_cell = []
    for i in range(3):
        theta_i = [angle, speed, t_release[i], t_delay[i]]
        single_time, intervals = calculate_single_flare_time(
            theta_i,
            r_M1_0,
            e_M1,
            v_M1,
            r_FY1_0,
            g,
            R_cloud,
            v_sink,
            cloud_lifetime,
            T_base,
            cylinder_radius,
            cylinder_height,
            t_range,
            dt,
        )
        single_times.append(single_time)
        intervals_cell.append(str(intervals))  # 以字符串形式存储区间列表

    # 汇总表
    results_df = pd.DataFrame(
        {
            "flare_id": [1, 2, 3],
            "t_release": t_release,
            "t_delay": t_delay,
            "t_explosion": t_explosion,
            "release_x": release_pos[:, 0],
            "release_y": release_pos[:, 1],
            "release_z": release_pos[:, 2],
            "explosion_x": explosion_pos[:, 0],
            "explosion_y": explosion_pos[:, 1],
            "explosion_z": explosion_pos[:, 2],
            "single_time": single_times,
            "intervals": intervals_cell,
        }
    )

    print("\n每枚烟幕弹的投放/起爆点与单独时长及区间:")
    print(results_df)

    # 保存到CSV
    output_path = "A题/Q3_flare_results.csv"
    results_df.to_csv(output_path, index=False)
    print(f"\n结果已保存到 {output_path}")
