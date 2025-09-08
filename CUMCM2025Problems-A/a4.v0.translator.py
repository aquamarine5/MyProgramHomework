import numpy as np
from scipy.optimize import differential_evolution
import time

# ===== 基本参数 =====
g = 9.8  # 重力加速度，m/s^2
v_M1 = 300  # 导弹M1速度，m/s
R_cloud = 10  # 烟幕云团半径，m
v_sink = 3  # 烟幕云团下沉速度，m/s
cloud_lifetime = 20  # 烟幕有效时间，s
cylinder_radius = 7  # 真目标圆柱体半径，m
cylinder_height = 10  # 真目标圆柱体高度，m

# ===== 初始位姿 =====
r_M1_0 = np.array([20000, 0, 2000])  # 导弹M1初始位置
O = np.array([0, 0, 0])  # 假目标位置（原点）
T_base = np.array([0, 200, 0])  # 真目标下底面圆心位置

# 三架无人机初始位置
r_FY1_0 = np.array([17800, 0, 1800])
r_FY2_0 = np.array([12000, 1400, 1400])
r_FY3_0 = np.array([6000, -3000, 700])

# 导弹飞行方向单位向量
e_M1 = (O - r_M1_0) / np.linalg.norm(O - r_M1_0)

# ===== 时间设置 =====
t_start = 0
t_end = 100  # 可按需收紧
dt = 0.05  # 仅用于生成时间网格
t_range = np.arange(t_start, t_end + dt, dt)

# ===== 生成圆柱体关键点：6 点全遮蔽判据 =====
n_points = 2  # 每个圆面取 2 个圆周点
key_points = np.zeros((2 * n_points + 2, 3))
# 底/顶圆心
key_points[0, :] = T_base
key_points[1, :] = T_base + np.array([0, 0, cylinder_height])
# 底面圆周点
for i in range(n_points):
    ang = 2 * np.pi * i / n_points
    key_points[2 + i, :] = T_base + cylinder_radius * np.array(
        [np.cos(ang), np.sin(ang), 0]
    )
# 顶面圆周点
for i in range(n_points):
    ang = 2 * np.pi * i / n_points
    key_points[2 + n_points + i, :] = (
        T_base
        + cylinder_radius * np.array([np.cos(ang), np.sin(ang), 0])
        + np.array([0, 0, cylinder_height])
    )

# ===== 估算导弹飞行时间 =====
dist_to_target = np.linalg.norm(r_M1_0 - T_base)
est_flight_time = dist_to_target / v_M1
print(f"估计导弹飞行时间: {est_flight_time:.2f} 秒")

# ===== 辅助函数 =====


def is_line_segment_intersect_sphere(p1, p2, center, radius):
    """判断线段 p1-p2 是否与球体相交"""
    if np.linalg.norm(p1 - center) <= radius or np.linalg.norm(p2 - center) <= radius:
        return True
    v = p2 - p1
    a = np.dot(v, v)
    b = 2 * np.dot(p1 - center, v)
    c = np.dot(p1 - center, p1 - center) - radius**2
    delta = b**2 - 4 * a * c
    if delta < 0:
        return False
    t1 = (-b + np.sqrt(delta)) / (2 * a)
    t2 = (-b - np.sqrt(delta)) / (2 * a)
    return (0 <= t1 <= 1) or (0 <= t2 <= 1)


def calculate_multiple_UAVs_shielding_time(
    theta,
    r_M1_0,
    e_M1,
    v_M1,
    r_FY1_0,
    r_FY2_0,
    r_FY3_0,
    g,
    R_cloud,
    v_sink,
    cloud_lifetime,
    key_points,
    t_range,
):
    """计算三架无人机协同投放的总有效遮蔽时间（供优化算法使用）"""
    angle1, speed1, t_release1, t_delay1 = theta[0:4]
    angle2, speed2, t_release2, t_delay2 = theta[4:8]
    angle3, speed3, t_release3, t_delay3 = theta[8:12]

    t_explosion1 = t_release1 + t_delay1
    t_explosion2 = t_release2 + t_delay2
    t_explosion3 = t_release3 + t_delay3

    e_FY1 = np.array([np.cos(angle1), np.sin(angle1), 0])
    e_FY2 = np.array([np.cos(angle2), np.sin(angle2), 0])
    e_FY3 = np.array([np.cos(angle3), np.sin(angle3), 0])

    r_FY1_release = r_FY1_0 + speed1 * t_release1 * e_FY1
    r_S1_explosion = (
        r_FY1_release
        + t_delay1 * speed1 * e_FY1
        - 0.5 * g * t_delay1**2 * np.array([0, 0, 1])
    )

    r_FY2_release = r_FY2_0 + speed2 * t_release2 * e_FY2
    r_S2_explosion = (
        r_FY2_release
        + t_delay2 * speed2 * e_FY2
        - 0.5 * g * t_delay2**2 * np.array([0, 0, 1])
    )

    r_FY3_release = r_FY3_0 + speed3 * t_release3 * e_FY3
    r_S3_explosion = (
        r_FY3_release
        + t_delay3 * speed3 * e_FY3
        - 0.5 * g * t_delay3**2 * np.array([0, 0, 1])
    )

    is_effective = np.zeros_like(t_range, dtype=bool)

    for i, t in enumerate(t_range):
        r_M1_t = r_M1_0 + v_M1 * t * e_M1

        clouds_active = []
        if t_explosion1 <= t <= t_explosion1 + cloud_lifetime:
            center = r_S1_explosion - v_sink * (t - t_explosion1) * np.array([0, 0, 1])
            clouds_active.append(center)
        if t_explosion2 <= t <= t_explosion2 + cloud_lifetime:
            center = r_S2_explosion - v_sink * (t - t_explosion2) * np.array([0, 0, 1])
            clouds_active.append(center)
        if t_explosion3 <= t <= t_explosion3 + cloud_lifetime:
            center = r_S3_explosion - v_sink * (t - t_explosion3) * np.array([0, 0, 1])
            clouds_active.append(center)

        if not clouds_active:
            continue

        all_key_points_covered = True
        for kp in key_points:
            is_kp_covered = False
            for cloud_center in clouds_active:
                if is_line_segment_intersect_sphere(r_M1_t, kp, cloud_center, R_cloud):
                    is_kp_covered = True
                    break
            if not is_kp_covered:
                all_key_points_covered = False
                break

        if all_key_points_covered:
            is_effective[i] = True

    effective_time = np.sum(is_effective) * (t_range[1] - t_range[0])
    return -effective_time  # differential_evolution 最小化，所以返回负值


def calculate_multiple_UAVs_shielding_details(
    theta,
    r_M1_0,
    e_M1,
    v_M1,
    r_FY1_0,
    r_FY2_0,
    r_FY3_0,
    g,
    R_cloud,
    v_sink,
    cloud_lifetime,
    key_points,
    t_range,
):
    """详细遮蔽效果（区间 + 主导UAV）"""
    angle1, speed1, t_release1, t_delay1 = theta[0:4]
    angle2, speed2, t_release2, t_delay2 = theta[4:8]
    angle3, speed3, t_release3, t_delay3 = theta[8:12]

    t_explosion1 = t_release1 + t_delay1
    t_explosion2 = t_release2 + t_delay2
    t_explosion3 = t_release3 + t_delay3

    explosions = [
        (
            t_explosion1,
            r_FY1_0
            + speed1 * t_release1 * np.array([np.cos(angle1), np.sin(angle1), 0])
            + t_delay1 * speed1 * np.array([np.cos(angle1), np.sin(angle1), 0])
            - 0.5 * g * t_delay1**2 * np.array([0, 0, 1]),
        ),
        (
            t_explosion2,
            r_FY2_0
            + speed2 * t_release2 * np.array([np.cos(angle2), np.sin(angle2), 0])
            + t_delay2 * speed2 * np.array([np.cos(angle2), np.sin(angle2), 0])
            - 0.5 * g * t_delay2**2 * np.array([0, 0, 1]),
        ),
        (
            t_explosion3,
            r_FY3_0
            + speed3 * t_release3 * np.array([np.cos(angle3), np.sin(angle3), 0])
            + t_delay3 * speed3 * np.array([np.cos(angle3), np.sin(angle3), 0])
            - 0.5 * g * t_delay3**2 * np.array([0, 0, 1]),
        ),
    ]

    is_effective = np.zeros_like(t_range, dtype=bool)
    effective_by_UAV = np.zeros((len(t_range), 3), dtype=int)

    for i, t in enumerate(t_range):
        r_M1_t = r_M1_0 + v_M1 * t * e_M1

        clouds_active = []
        cloud_indices = []
        for idx, (t_exp, r_exp) in enumerate(explosions):
            if t_exp <= t <= t_exp + cloud_lifetime:
                center = r_exp - v_sink * (t - t_exp) * np.array([0, 0, 1])
                clouds_active.append(center)
                cloud_indices.append(idx)

        if not clouds_active:
            continue

        all_key_points_covered = True
        for kp in key_points:
            is_kp_covered = False
            for cloud_center in clouds_active:
                if is_line_segment_intersect_sphere(r_M1_t, kp, cloud_center, R_cloud):
                    is_kp_covered = True
                    break
            if not is_kp_covered:
                all_key_points_covered = False
                break

        if all_key_points_covered:
            is_effective[i] = True
            # 简单地将贡献归于最后一个激活的无人机
            if cloud_indices:
                effective_by_UAV[i, cloud_indices[-1]] = 1

    effective_indices = np.where(is_effective)[0]
    if len(effective_indices) == 0:
        print("无有效遮蔽时间")
        return 0, [], [], []

    intervals = []
    main_UAVs = []
    start_idx = effective_indices[0]

    for i in range(1, len(effective_indices)):
        if effective_indices[i] != effective_indices[i - 1] + 1:
            end_idx = effective_indices[i - 1]
            intervals.append((t_range[start_idx], t_range[end_idx]))

            block = effective_by_UAV[start_idx : end_idx + 1]
            counts = np.sum(block, axis=0)
            main_UAVs.append(np.argmax(counts) + 1 if np.sum(counts) > 0 else 0)

            start_idx = effective_indices[i]

    end_idx = effective_indices[-1]
    intervals.append((t_range[start_idx], t_range[end_idx]))
    block = effective_by_UAV[start_idx : end_idx + 1]
    counts = np.sum(block, axis=0)
    main_UAVs.append(np.argmax(counts) + 1 if np.sum(counts) > 0 else 0)

    total_duration = sum(end - start for start, end in intervals)

    print("有效遮蔽时间区间：")
    for k, ((start, end), uav) in enumerate(zip(intervals, main_UAVs)):
        print(
            f"区间 {k+1}: {start:.2f} - {end:.2f} s，持续 {end-start:.2f} s，主要由 FY{uav} 提供"
        )
    print(f"总有效遮蔽时长: {total_duration:.2f} s")

    return total_duration, intervals, main_UAVs


# ===== GA/DE 目标函数 =====
def fitness_function(theta):
    return calculate_multiple_UAVs_shielding_time(
        theta,
        r_M1_0,
        e_M1,
        v_M1,
        r_FY1_0,
        r_FY2_0,
        r_FY3_0,
        g,
        R_cloud,
        v_sink,
        cloud_lifetime,
        key_points,
        t_range,
    )


# 变量边界：[angle, speed, release, delay] × 3
bounds = [
    (0, 2 * np.pi),
    (70, 140),
    (0, 67),
    (0.5, 20),  # UAV1
    (0, 2 * np.pi),
    (70, 140),
    (0, 67),
    (0.5, 20),  # UAV2
    (0, 2 * np.pi),
    (70, 140),
    (0, 67),
    (0.5, 20),  # UAV3
]

# ===== 运行差分进化算法 =====
start_time = time.time()
result = differential_evolution(
    fitness_function,
    bounds,
    strategy="best1bin",
    maxiter=10,  # 对应 MaxGenerations
    popsize=15,  # 对应 PopulationSize, popsize * len(bounds) = 15 * 12 = 180, 接近200
    tol=0.01,
    recombination=0.8,  # 对应 CrossoverFraction
    disp=True,  # 对应 Display: 'iter'
    workers=1,  # 使用所有可用核心
)
end_time = time.time()
print(f"优化用时: {end_time - start_time:.2f} 秒")


# ===== 解析最优解 =====
optimal_params = result.x
fval = result.fun

angle1, speed1, release_time1, delay_time1 = optimal_params[0:4]
angle2, speed2, release_time2, delay_time2 = optimal_params[4:8]
angle3, speed3, release_time3, delay_time3 = optimal_params[8:12]

angle1_deg, angle2_deg, angle3_deg = np.rad2deg([angle1, angle2, angle3])
explosion_time1 = release_time1 + delay_time1
explosion_time2 = release_time2 + delay_time2
explosion_time3 = release_time3 + delay_time3

e_FY1 = np.array([np.cos(angle1), np.sin(angle1), 0])
e_FY2 = np.array([np.cos(angle2), np.sin(angle2), 0])
e_FY3 = np.array([np.cos(angle3), np.sin(angle3), 0])

release_pos1 = r_FY1_0 + speed1 * release_time1 * e_FY1
explosion_pos1 = (
    release_pos1
    + delay_time1 * speed1 * e_FY1
    - 0.5 * g * delay_time1**2 * np.array([0, 0, 1])
)

release_pos2 = r_FY2_0 + speed2 * release_time2 * e_FY2
explosion_pos2 = (
    release_pos2
    + delay_time2 * speed2 * e_FY2
    - 0.5 * g * delay_time2**2 * np.array([0, 0, 1])
)

release_pos3 = r_FY3_0 + speed3 * release_time3 * e_FY3
explosion_pos3 = (
    release_pos3
    + delay_time3 * speed3 * e_FY3
    - 0.5 * g * delay_time3**2 * np.array([0, 0, 1])
)

print("\n最优参数:")
print(
    f"FY1: 角度 {angle1_deg:.2f}°({angle1:.2f} rad), 速度 {speed1:.2f}, 投放 {release_time1:.2f}s, 延时 {delay_time1:.2f}s, 起爆 {explosion_time1:.2f}s"
)
print(
    f"FY2: 角度 {angle2_deg:.2f}°({angle2:.2f} rad), 速度 {speed2:.2f}, 投放 {release_time2:.2f}s, 延时 {delay_time2:.2f}s, 起爆 {explosion_time2:.2f}s"
)
print(
    f"FY3: 角度 {angle3_deg:.2f}°({angle3:.2f} rad), 速度 {speed3:.2f}, 投放 {release_time3:.2f}s, 延时 {delay_time3:.2f}s, 起爆 {explosion_time3:.2f}s"
)

print(
    f"FY1 投放点: ({release_pos1[0]:.2f}, {release_pos1[1]:.2f}, {release_pos1[2]:.2f}), 起爆点: ({explosion_pos1[0]:.2f}, {explosion_pos1[1]:.2f}, {explosion_pos1[2]:.2f})"
)
print(
    f"FY2 投放点: ({release_pos2[0]:.2f}, {release_pos2[1]:.2f}, {release_pos2[2]:.2f}), 起爆点: ({explosion_pos2[0]:.2f}, {explosion_pos2[1]:.2f}, {explosion_pos2[2]:.2f})"
)
print(
    f"FY3 投放点: ({release_pos3[0]:.2f}, {release_pos3[1]:.2f}, {release_pos3[2]:.2f}), 起爆点: ({explosion_pos3[0]:.2f}, {explosion_pos3[1]:.2f}, {explosion_pos3[2]:.2f})"
)

total_effective_time = -fval
print(f"总有效遮蔽时间: {total_effective_time:.2f} 秒")

# ===== 详细遮蔽区间与主导UAV =====
calculate_multiple_UAVs_shielding_details(
    optimal_params,
    r_M1_0,
    e_M1,
    v_M1,
    r_FY1_0,
    r_FY2_0,
    r_FY3_0,
    g,
    R_cloud,
    v_sink,
    cloud_lifetime,
    key_points,
    t_range,
)
