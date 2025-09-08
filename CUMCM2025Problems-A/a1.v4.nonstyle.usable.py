from warnings import deprecated
import numba
import numpy as np
import numpy as npy
from typing import List
from tqdm import tqdm
from numpy.typing import NDArray

Vector3 = NDArray[npy.float64]
g = 9.8
v_missile = 300
v_smoke_sink = 3
effective_radius = 10
effective_duration = 20

# 目标位置
fake_target = np.array([0, 0, 0])

# 导弹M1初始位置
M1_start = np.array([20000, 0, 2000])

# 无人机FY1初始位置
FY1_start = np.array([17800, 0, 1800])

# 无人机速度
v_drone = 120
direction_to_target = fake_target[:2] - FY1_start[:2]
direction_to_target = direction_to_target / np.linalg.norm(direction_to_target)
v_drone_vector = np.array(
    [v_drone * direction_to_target[0], v_drone * direction_to_target[1], 0]
)

# 时间参数
t_drop = 1.5
t_blast_delay = 3.6
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


# ================= 工具函数 =================
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


def calculate_effective_intervals():
    t_missile_to_target = (fake_target[0] - M1_start[0]) / v_missile_vector[0]
    start_time = 0
    end_time = min(effective_duration, t_missile_to_target - t_blast)
    if end_time <= 0:
        return [], 0.0

    time_step = 0.0001
    intervals = []
    total_effective_time = 0.0

    in_cover = False
    cover_start = None

    num_steps = int((end_time - start_time) / time_step)
    for i in tqdm(range(num_steps + 1), desc="计算有效遮蔽区间"):
        current_time = start_time + i * time_step
        t_missile = t_blast + current_time
        pos_missile = missile_position(t_missile)
        pos_smoke = smoke_position(current_time)

        # 遍历6个点，必须全部遮蔽才算有效
        all_covered = True
        for pt in get6points(current_time):
            missile_to_target_direction = pt - pos_missile
            missile_to_target_direction = missile_to_target_direction / np.linalg.norm(
                missile_to_target_direction
            )
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
                # 刚进入遮蔽区
                cover_start = current_time
                in_cover = True
            total_effective_time += time_step
        else:
            if in_cover:
                # 结束遮蔽区
                intervals.append((cover_start, current_time))
                in_cover = False

    # 如果最后还在遮蔽状态
    if in_cover:
        intervals.append((cover_start, end_time))

    return intervals, total_effective_time


# ================= 主程序 =================
intervals, total_time = calculate_effective_intervals()

print("\n=== 第一问计算结果（6点全部遮蔽判定）===")
print(f"烟幕弹投放时间: {t_drop:.6f} s")
print(f"烟幕弹起爆时间: {t_blast:.6f} s")
print(
    f"起爆点位置: ({blast_position[0]:.6f}, {blast_position[1]:.6f}, {blast_position[2]:.6f})"
)
print(f"有效遮蔽总时长: {total_time:.6f} 秒")

if intervals:
    print("\n有效遮蔽区间：")
    for i, (s, e) in enumerate(intervals, 1):
        print(f"  区间 {i}: 起爆后 {s:.6f}s ~ {e:.6f}s")
else:
    print("\n没有形成有效遮蔽。")
