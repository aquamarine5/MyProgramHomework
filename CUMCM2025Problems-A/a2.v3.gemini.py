import sys
from warnings import deprecated
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numba
from typing import List
from numpy.typing import NDArray
import numpy as npy

Vector3 = NDArray[npy.float64]


def calculate_smoke_obscuration(
    drone_direction, drone_speed, drop_time, blast_delay, visualize=False, verbose=False
):
    """
    计算烟幕干扰弹对导弹M1的有效遮蔽时间 (6点严格判定版，带遮蔽区间输出)

    返回:
    effective_time: 有效遮蔽时间 (s)
    intervals: 遮蔽区间列表 [(start, end), ...]，时间相对起爆后
    """

    # ================= 基本常量 =================
    g = 9.8
    v_missile = 300
    v_smoke_sink = 3
    effective_radius = 10
    effective_duration = 20

    # 目标位置（假目标固定）
    fake_target = np.array([0, 0, 0])

    # 导弹M1初始位置
    M1_start = np.array([20000, 0, 2000])

    # 无人机FY1初始位置
    FY1_start = np.array([17800, 0, 1800])

    # 标准化无人机方向向量
    drone_direction = np.array(drone_direction)
    if np.linalg.norm(drone_direction) > 0:
        drone_direction = drone_direction / np.linalg.norm(drone_direction)

    # 无人机速度向量
    v_drone_vector = drone_speed * drone_direction

    # 时间参数
    t_drop = drop_time
    t_blast_delay = blast_delay
    t_blast = t_drop + t_blast_delay

    # 计算投放点与起爆点
    drop_position = FY1_start + v_drone_vector * t_drop
    vertical_drop = 0.5 * g * t_blast_delay**2
    blast_position = np.array(
        [
            drop_position[0] + v_drone_vector[0] * t_blast_delay,
            drop_position[1] + v_drone_vector[1] * t_blast_delay,
            drop_position[2] - vertical_drop,
        ]
    )

    # 导弹飞行方向（指向假目标）
    missile_direction = fake_target - M1_start
    missile_direction = missile_direction / np.linalg.norm(missile_direction)
    v_missile_vector = v_missile * missile_direction

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
        cx = 1400 / (
            npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
        )
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
        gx = 1400 / (
            npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
        )
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

    # ================ 真目标6个点（随时间变化） ================
    @deprecated("Use get6points instead")
    def target_points(t):
        pts = []
        X = 20000 - 3000 * np.sqrt(101) / 101 * t

        # 上底圆 z=10
        x1 = 1400 * X / np.sqrt(X**2 + 40000)
        y1 = 200 - 1400 / np.sqrt(X**2 + 40000)
        pts.append(np.array([x1, y1, 10]))

        denom1 = np.sqrt(200**2 + X**2)
        x2 = 1400 / denom1
        y2 = 200 + 7 * X / denom1
        pts.append(np.array([x2, y2, 10]))
        pts.append(np.array([x2, -y2 + 400, 10]))

        # 下底圆 z=0
        x3 = 1400 * X / np.sqrt(X**2 + 200**2)
        y3 = 200 - 1400 / np.sqrt(X**2 + 200**2)
        pts.append(np.array([x3, y3, 0]))

        denom2 = np.sqrt(200**2 + X**2)
        x4 = 1400 / denom2
        y4 = 200 + 7 * X / denom2
        pts.append(np.array([x4, y4, 0]))
        pts.append(np.array([x4, -y4 + 400, 0]))

        return pts

    # ================ 工具函数 ================
    def missile_position(t):
        return M1_start + v_missile_vector * t

    def smoke_position(t_smoke):
        return np.array(
            [
                blast_position[0],
                blast_position[1],
                blast_position[2] - v_smoke_sink * t_smoke,
            ]
        )

    def distance_point_to_line(point, line_point, line_direction):
        ap = point - line_point
        projection = np.dot(ap, line_direction) / np.linalg.norm(line_direction)
        foot_point = line_point + projection * line_direction
        return np.linalg.norm(point - foot_point)

    def is_smoke_between(missile_pos, smoke_pos, target_pos):
        missile_to_smoke = smoke_pos - missile_pos
        missile_to_target = target_pos - missile_pos
        return np.dot(missile_to_smoke, missile_to_target) > 0

    # ================ 遮蔽时长计算（严格6点） ================
    def time_to_target(position, velocity, target):
        t_x = (target[0] - position[0]) / velocity[0]
        return t_x

    t_missile_to_target = time_to_target(M1_start, v_missile_vector, fake_target)

    start_time = 0
    end_time = min(effective_duration, t_missile_to_target - t_blast)
    if end_time <= 0:
        return 0.0, []

    time_step = 0.01
    total_effective_time = 0.0
    intervals = []
    in_cover = False
    cover_start = None

    current_time = start_time
    while current_time <= end_time:
        t_missile = t_blast + current_time
        pos_missile = missile_position(t_missile)
        pos_smoke = smoke_position(current_time)

        # 遍历6个点，必须全部遮蔽才算有效
        all_covered = True
        for pt in get6points(current_time):
            missile_to_target_direction = pt - pos_missile
            missile_to_target_direction /= np.linalg.norm(missile_to_target_direction)
            distance = distance_point_to_line(
                pos_smoke, pos_missile, missile_to_target_direction
            )
            is_between = is_smoke_between(pos_missile, pos_smoke, pt)
            in_smoke = np.linalg.norm(pos_missile - pos_smoke) <= effective_radius

            if not ((distance <= effective_radius and is_between) or in_smoke):
                all_covered = False
                break

        if all_covered:
            if not in_cover:
                cover_start = current_time
                in_cover = True
            total_effective_time += time_step
        else:
            if in_cover:
                intervals.append((cover_start, current_time))
                in_cover = False

        current_time += time_step

    if in_cover:
        intervals.append((cover_start, end_time))

    if verbose:
        print(f"有效遮蔽总时长 (6点严格): {total_effective_time:.6f} 秒")
        if intervals:
            print("有效遮蔽区间 (相对起爆后):")
            for i, (s, e) in enumerate(intervals, 1):
                print(f"  区间 {i}: {s:.6f} s ~ {e:.6f} s")
        else:
            print("未形成有效遮蔽。")

    return total_effective_time, intervals


import numpy as np
from scipy.optimize import basinhopping, minimize
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# 目标函数（返回负的有效时间，因为我们要最小化）
def objective(params):
    theta, s, t_drop, t_delay = params
    u = np.cos(theta / 10)
    v = np.sin(theta / 10)
    dir_vec = [u, v, 0]

    effective_time, _ = calculate_smoke_obscuration(  # 只取第一个
        drone_direction=dir_vec,
        drone_speed=s,
        drop_time=t_drop / 10,
        blast_delay=t_delay / 10,
        visualize=False,
        verbose=False,
    )

    return -effective_time  # 返回负值以便最小化


# 自定义回调函数用于记录优化过程
class OptimizationTracker:
    def __init__(self):
        self.history = []  # 记录所有函数值
        self.params_history = []  # 记录所有参数
        self.best_history = []  # 记录最佳函数值
        self.best_params_history = []  # 记录最佳参数
        self.best_value = float("inf")
        self.best_params = None

    def __call__(self, x, f, accepted):
        self.history.append(f)
        self.params_history.append(x.copy())

        if f < self.best_value:
            self.best_value = f
            self.best_params = x.copy()

        self.best_history.append(self.best_value)
        self.best_params_history.append(self.best_params.copy())

        if len(self.history) % 10 == 0:
            print(
                f"Iteration {len(self.history)}: Current value = {-f:.4f}, Best value = {-self.best_value:.4f}"
            )


# 变量边界
bounds = [(np.pi * 9, np.pi * 11), (70, 140), (0, 50), (0.1, 50)]

# 初始参数
initial_params = np.array([np.pi * 10, 120, 5, 35])

# 创建跟踪器
tracker = OptimizationTracker()
i = calculate_smoke_obscuration(
    drone_direction=[-1, 0, 0],
    drone_speed=120,
    drop_time=0.5,
    blast_delay=3.5,
)
print(i)
sys.exit(0)
# 模拟退火优化
print("开始模拟退火优化...")
minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds, "options": {"maxiter": 100}}

result_sa = basinhopping(
    objective,
    initial_params,
    niter=1000,
    minimizer_kwargs=minimizer_kwargs,
    stepsize=0.5,
    accept_test=None,
    callback=tracker,
)

# 提取最佳参数
best_params_sa = result_sa.x
best_value_sa = -result_sa.fun  # 转换为正的有效时间

print("\n模拟退火优化结果:")
print(f"最佳方向角度 (theta): {best_params_sa[0]:.4f} rad")
print(f"最佳速度: {best_params_sa[1]:.2f} m/s")
print(f"最佳投放时间: {best_params_sa[2]:.2f} s")
print(f"最佳起爆延迟: {best_params_sa[3]:.2f} s")
print(f"最大有效遮蔽时间: {best_value_sa:.4f} s")

# 绘制收敛曲线
plt.figure(figsize=(15, 5))

# 1. 损失函数曲线
plt.subplot(1, 3, 1)
iterations = range(1, len(tracker.history) + 1)
plt.plot(iterations, [-x for x in tracker.history], "b-", alpha=0.7, label="当前值")
plt.plot(
    iterations, [-x for x in tracker.best_history], "r-", linewidth=2, label="最佳值"
)
plt.xlabel("迭代次数")
plt.ylabel("有效遮蔽时间 (s)")
plt.title("优化过程 - 损失函数曲线")
plt.legend()
plt.grid(True, alpha=0.3)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# 2. 参数变化曲线（归一化显示）
plt.subplot(1, 3, 2)

# 使用tracker中的参数历史记录
theta_norm = [
    (p[0] - bounds[0][0]) / (bounds[0][1] - bounds[0][0])
    for p in tracker.params_history
]
speed_norm = [
    (p[1] - bounds[1][0]) / (bounds[1][1] - bounds[1][0])
    for p in tracker.params_history
]
drop_norm = [
    (p[2] - bounds[2][0]) / (bounds[2][1] - bounds[2][0])
    for p in tracker.params_history
]
delay_norm = [
    (p[3] - bounds[3][0]) / (bounds[3][1] - bounds[3][0])
    for p in tracker.params_history
]

plt.plot(iterations, theta_norm, label="方向角度", alpha=0.7)
plt.plot(iterations, speed_norm, label="速度", alpha=0.7)
plt.plot(iterations, drop_norm, label="投放时间", alpha=0.7)
plt.plot(iterations, delay_norm, label="起爆延迟", alpha=0.7)

plt.xlabel("迭代次数")
plt.ylabel("归一化参数值")
plt.title("参数优化过程")
plt.legend()
plt.grid(True, alpha=0.3)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# 3. 最终结果对比
plt.subplot(1, 3, 3)
initial_value = -objective(initial_params)
plt.bar(["初始参数", "优化后参数"], [initial_value, best_value_sa], alpha=0.7)
plt.ylabel("有效遮蔽时间 (s)")
plt.title("优化前后对比")
plt.grid(True, alpha=0.3)

# 在柱状图上添加数值标签
for i, v in enumerate([initial_value, best_value_sa]):
    plt.text(i, v + 0.1, f"{v:.2f}s", ha="center", va="bottom")

plt.tight_layout()
plt.show()

# 输出详细的最佳参数信息
print("\n详细最佳参数信息:")
print(
    f"方向向量: [{np.cos(best_params_sa[0]/10):.4f}, {np.sin(best_params_sa[0]/10):.4f}, 0]"
)
print(f"速度: {best_params_sa[1]:.2f} m/s (范围: 70-140 m/s)")
print(f"投放时间: {best_params_sa[2]/10:.2f} s (范围: 0-5 s)")
print(f"起爆延迟: {best_params_sa[3]/10:.2f} s (范围: 0.1-5 s)")
print(
    f"优化提升: {(best_value_sa - initial_value):.2f} s ({((best_value_sa - initial_value)/initial_value*100):.1f}%)"
)

# 输出最佳参数对应的具体值
print("\n最佳策略:")
print(
    f"无人机飞行方向: 角度 {best_params_sa[0]:.4f} rad (约 {np.degrees(best_params_sa[0]):.2f}°)"
)
print(f"无人机飞行速度: {best_params_sa[1]:.2f} m/s")
print(f"烟幕干扰弹投放点: 在任务开始后 {best_params_sa[2]:.2f} s 投放")
print(f"烟幕干扰弹起爆点: 投放后 {best_params_sa[3]:.2f} s 起爆")
print(f"预计有效遮蔽时间: {best_value_sa:.2f} s")
