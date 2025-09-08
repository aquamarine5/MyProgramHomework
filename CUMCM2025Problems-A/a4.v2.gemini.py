import numpy as np
from sko.GA import GA

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
dt = 0.05  # 时间步长
t_range = np.arange(t_start, t_end, dt)

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
    # 端点在球内快速命中
    if np.linalg.norm(p1 - center) <= radius or np.linalg.norm(p2 - center) <= radius:
        return True
    v = p2 - p1
    a = np.dot(v, v)
    b = 2 * np.dot(p1 - center, v)
    c = np.dot(p1 - center, p1 - center) - radius**2
    D = b**2 - 4 * a * c
    if D < 0:
        return False
    t1 = (-b + np.sqrt(D)) / (2 * a)
    t2 = (-b - np.sqrt(D)) / (2 * a)
    return (0 <= t1 <= 1) or (0 <= t2 <= 1)


# ===== GA 目标函数 =====
def calculate_multiple_UAVs_shielding_time(theta):
    """计算三架无人机协同投放的总有效遮蔽时间"""
    (
        angle1,
        speed1,
        t_release1,
        t_delay1,
        angle2,
        speed2,
        t_release2,
        t_delay2,
        angle3,
        speed3,
        t_release3,
        t_delay3,
    ) = theta

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

        clouds_exist_this_moment = []
        # Cloud 1
        if t_explosion1 <= t <= t_explosion1 + cloud_lifetime:
            center = r_S1_explosion - v_sink * (t - t_explosion1) * np.array([0, 0, 1])
            clouds_exist_this_moment.append(center)
        # Cloud 2
        if t_explosion2 <= t <= t_explosion2 + cloud_lifetime:
            center = r_S2_explosion - v_sink * (t - t_explosion2) * np.array([0, 0, 1])
            clouds_exist_this_moment.append(center)
        # Cloud 3
        if t_explosion3 <= t <= t_explosion3 + cloud_lifetime:
            center = r_S3_explosion - v_sink * (t - t_explosion3) * np.array([0, 0, 1])
            clouds_exist_this_moment.append(center)

        if not clouds_exist_this_moment:
            continue

        all_key_points_covered = True
        for kp in key_points:
            point_is_covered = False
            for cloud_center in clouds_exist_this_moment:
                if is_line_segment_intersect_sphere(r_M1_t, kp, cloud_center, R_cloud):
                    point_is_covered = True
                    break
            if not point_is_covered:
                all_key_points_covered = False
                break

        if all_key_points_covered:
            is_effective[i] = True

    effective_time = np.sum(is_effective) * dt
    # GA in scikit-opt finds the minimum, so we return the negative of the value to maximize.
    return -effective_time


# ===== GA 设置 =====
# 变量边界：[angle, speed, release, delay] × 3
lb = [0, 70, 0, 0.5, 0, 70, 0, 0.5, 0, 70, 0, 0.5]
ub = [2 * np.pi, 140, 67, 20, 2 * np.pi, 140, 67, 20, 2 * np.pi, 140, 67, 20]

ga = GA(
    func=calculate_multiple_UAVs_shielding_time,
    n_dim=12,
    size_pop=200,
    max_iter=10,  # 建议增加迭代次数以获得更好结果，例如 100
    prob_mut=0.01,  # 变异概率
    lb=lb,
    ub=ub,
    precision=1e-7,
)

# ===== 运行 GA =====
best_params, fval = ga.run()

# ===== 解析最优解 =====
(
    angle1,
    speed1,
    release_time1,
    delay_time1,
    angle2,
    speed2,
    release_time2,
    delay_time2,
    angle3,
    speed3,
    release_time3,
    delay_time3,
) = best_params

angle1_deg = np.rad2deg(angle1)
angle2_deg = np.rad2deg(angle2)
angle3_deg = np.rad2deg(angle3)

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

total_effective_time = -fval[0]
print(f"总有效遮蔽时间: {total_effective_time:.2f} 秒")

# 可以在这里添加详细遮蔽区间分析和绘图代码
# ...
