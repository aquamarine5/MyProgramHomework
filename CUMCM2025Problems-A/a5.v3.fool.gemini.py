import datetime
import sys
from time import time
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Optional, Tuple
import pandas as pd
from sko.GA import GA
from tqdm import tqdm
from sko.tools import set_run_mode

# ================== 初始化参数 (与v1/v2版本相同) ==================
Vector3 = NDArray[npy.float64]
G = 9.8  # 重力加速度
# 导弹参数
v_missile = 300.0
pos_M1_0 = npy.array([20000.0, 0.0, 2000.0])
pos_M2_0 = npy.array([19000.0, 600.0, 2100.0])
pos_M3_0 = npy.array([18000.0, -600.0, 1900.0])
pos_missiles_0 = npy.array([pos_M1_0, pos_M2_0, pos_M3_0])
pos_missile_target = npy.array([0.0, 0.0, 0.0])
e_missiles = (pos_missile_target - pos_missiles_0) / npy.linalg.norm(
    pos_missile_target - pos_missiles_0, axis=1, keepdims=True
)

# 目标参数
pos_real_target = npy.array([0.0, 200.0, 0.0])
r_real_target = 7.0
h_real_target = 10.0

# 无人机参数
pos_FY1_0 = npy.array([17800.0, 0.0, 1800.0])
pos_FY2_0 = npy.array([12000.0, 1400.0, 1400.0])
pos_FY3_0 = npy.array([6000.0, -3000.0, 700.0])
pos_FY4_0 = npy.array([11000.0, 2000.0, 1800.0])
pos_FY5_0 = npy.array([13000.0, -2000.0, 1300.0])
pos_UAVs_0 = npy.array([pos_FY1_0, pos_FY2_0, pos_FY3_0, pos_FY4_0, pos_FY5_0])
speed_FY_min = 70.0
speed_FY_max = 140.0
min_interval = 1.0

# 烟幕参数
r_cloud = 10.0
v_sink = 3.0
cloud_lifetime = 20.0

# 仿真参数
DT = 0.1
t_calculate_range = npy.arange(0.0, 100.0, DT, dtype=npy.float32)


# ================== 核心计算函数 (与v1/v2版本相同, Numba JIT) ==================
@numba.njit(cache=True)
def get_missile_position(t: float, missile_idx: int) -> Vector3:
    return pos_missiles_0[missile_idx] + v_missile * t * e_missiles[missile_idx]


@numba.njit(cache=True)
def get_cloud_position(t: float, pos_detonate: Vector3, t_detonate: float) -> Vector3:
    return npy.array(
        [
            pos_detonate[0],
            pos_detonate[1],
            pos_detonate[2] - v_sink * (t - t_detonate),
        ]
    )


@numba.njit(cache=True)
def distance_point_to_line_segment(p1: Vector3, p2: Vector3, p3: Vector3) -> float:
    line_vec = p2 - p1
    point_vec = p3 - p1
    dot = npy.dot(line_vec, point_vec)
    len_sq = npy.dot(line_vec, line_vec)
    if len_sq == 0.0:
        return npy.linalg.norm(p3 - p1)
    t = max(0.0, min(1.0, dot / len_sq))
    closest_point = p1 + t * line_vec
    return npy.linalg.norm(p3 - closest_point)


@numba.njit(cache=True)
def is_line_segment_intersect_sphere(
    p1: Vector3, p2: Vector3, sphere_center: Vector3, sphere_radius: float
) -> bool:
    return distance_point_to_line_segment(p1, p2, sphere_center) <= sphere_radius


@numba.njit(cache=True)
def get_target_key_points(pos_missile_now: Vector3) -> List[Vector3]:
    key_points = []
    key_points.append(pos_real_target)
    key_points.append(pos_real_target + npy.array([0.0, 0.0, h_real_target]))
    sight_vec_2d = pos_missile_now[:2] - pos_real_target[:2]
    if npy.linalg.norm(sight_vec_2d) == 0:  # 避免除零错误
        return key_points
    sight_dir_2d = sight_vec_2d / npy.linalg.norm(sight_vec_2d)
    for sign in [-1.0, 1.0]:
        offset = sign * r_real_target * sight_dir_2d
        key_points.append(
            npy.array(
                [pos_real_target[0] + offset[0], pos_real_target[1] + offset[1], 0.0]
            )
            + pos_real_target
        )
        key_points.append(
            npy.array(
                [
                    pos_real_target[0] + offset[0],
                    pos_real_target[1] + offset[1],
                    h_real_target,
                ]
            )
            + pos_real_target
        )
    return key_points


# ================== 协同优化目标函数 ==================
@numba.njit(cache=True)
def evaluate_collaborative_strategy(params: NDArray) -> float:
    """
    评估5架无人机协同策略的总遮蔽时间
    params: 长度为40的向量，包含5架无人机的所有参数
    """
    num_uavs = 5
    vars_per_uav = 8
    num_flares_per_uav = 3

    # 解析所有无人机和烟幕弹的参数
    all_detonate_times = npy.zeros((num_uavs, num_flares_per_uav))
    all_detonate_pos = npy.zeros((num_uavs, num_flares_per_uav, 3))

    for i in range(num_uavs):
        uav_params = params[i * vars_per_uav : (i + 1) * vars_per_uav]
        (
            direction_angle,
            speed,
            t_release1,
            t_span12,
            t_span23,
            t_delay1,
            t_delay2,
            t_delay3,
        ) = uav_params

        t_release = npy.array(
            [t_release1, t_release1 + t_span12, t_release1 + t_span12 + t_span23]
        )
        t_delay = npy.array([t_delay1, t_delay2, t_delay3])
        all_detonate_times[i, :] = t_release + t_delay

        direction_uav = npy.array(
            [npy.cos(direction_angle), npy.sin(direction_angle), 0.0]
        )
        v_uav = speed * direction_uav

        for j in range(num_flares_per_uav):
            pos_release_j = pos_UAVs_0[i] + v_uav * t_release[j]
            all_detonate_pos[i, j, :] = (
                pos_release_j
                + v_uav * t_delay[j]
                - 0.5 * G * t_delay[j] ** 2 * npy.array([0.0, 0.0, 1.0])
            )

    total_masked_time = 0.0

    # 对每个导弹计算
    for m_idx in range(len(pos_missiles_0)):
        is_masked_list = npy.zeros(len(t_calculate_range), dtype=npy.bool_)

        for t_idx, t_now in enumerate(t_calculate_range):
            pos_missile_now = get_missile_position(t_now, m_idx)

            # 找到当前时间所有有效的烟幕
            active_clouds = []
            for i in range(num_uavs):
                for j in range(num_flares_per_uav):
                    if (
                        all_detonate_times[i, j]
                        <= t_now
                        <= all_detonate_times[i, j] + cloud_lifetime
                    ):
                        active_clouds.append(
                            get_cloud_position(
                                t_now,
                                all_detonate_pos[i, j, :],
                                all_detonate_times[i, j],
                            )
                        )

            if not active_clouds:
                continue

            # 检查所有关键点是否都被遮蔽
            key_points = get_target_key_points(pos_missile_now)
            all_points_blocked = True
            for kp in key_points:
                is_kp_blocked = False
                for cloud_center in active_clouds:
                    if is_line_segment_intersect_sphere(
                        pos_missile_now, kp, cloud_center, r_cloud
                    ):
                        is_kp_blocked = True
                        break
                if not is_kp_blocked:
                    all_points_blocked = False
                    break

            if all_points_blocked:
                is_masked_list[t_idx] = True

        total_masked_time += npy.sum(is_masked_list) * DT

    return -total_masked_time  # GA求最小值，所以取负


# ================== 主优化流程 ==================
if __name__ == "__main__":
    num_uavs = 5
    vars_per_uav = 8
    total_vars = num_uavs * vars_per_uav

    # 设置所有40个变量的搜索边界
    lb_single = [0, speed_FY_min, 0, min_interval, min_interval, 0.5, 0.5, 0.5]
    ub_single = [2 * npy.pi, speed_FY_max, 60, 20, 20, 10, 10, 10]
    lb = lb_single * num_uavs
    ub = ub_single * num_uavs
    TOTAL_COUNT = 800

    progressBarState = tqdm(total=TOTAL_COUNT, desc="GA Progress")

    currentMaxCoverTime = [-1]
    set_run_mode(evaluate_collaborative_strategy, "multithreading")

    def onProgressNext(gaInstance: GA):
        progressBarState.update(1)
        if not gaInstance.generation_best_Y:
            return
        currentMaxCoverTime[0] = max(
            currentMaxCoverTime[0], -(gaInstance.generation_best_Y[-1])
        )
        progressBarState.set_postfix({"best": f"{currentMaxCoverTime[0]:.2f}s"})

    class ProgressedGA(GA):
        def crossover(self):
            onProgressNext(self)
            return super().crossover()

    # 遗传算法参数
    ga = ProgressedGA(
        func=evaluate_collaborative_strategy,
        n_dim=total_vars,
        size_pop=200,  # 协同优化问题更复杂，需要更大的种群
        max_iter=500,  # 以及更多的迭代次数
        prob_mut=0.01,
        lb=lb,
        ub=ub,
        precision=1e-7,
    )
    progressBarState.close()
    print(
        f"\n======== 开始协同优化所有 {num_uavs} 架无人机 ({total_vars}个变量) ========"
    )
    best_params, best_value = ga.run()

    print("\n======== 协同优化完成 ========")
    print(f"  - 最优总遮蔽时间: {-best_value} s")

    # ================== 结果汇总与保存 ==================
    print("\n======== 开始汇总结果 ========")

    results_data = []
    for i in range(num_uavs):
        params = best_params[i * vars_per_uav : (i + 1) * vars_per_uav]
        (
            direction_angle,
            speed,
            t_release1,
            t_span12,
            t_span23,
            t_delay1,
            t_delay2,
            t_delay3,
        ) = params

        t_release = npy.array(
            [t_release1, t_release1 + t_span12, t_release1 + t_span12 + t_span23]
        )
        t_delay = npy.array([t_delay1, t_delay2, t_delay3])

        direction_uav = npy.array(
            [npy.cos(direction_angle), npy.sin(direction_angle), 0.0]
        )
        v_uav = speed * direction_uav

        for j in range(3):  # 每架无人机3枚弹
            pos_release = pos_UAVs_0[i] + v_uav * t_release[j]
            pos_detonate = (
                pos_release
                + v_uav * t_delay[j]
                - 0.5 * G * t_delay[j] ** 2 * npy.array([0.0, 0.0, 1.0])
            )

            results_data.append(
                {
                    "无人机编号": f"FY{i+1}",
                    "烟幕弹编号": j + 1,
                    "无人机运动方向(rad)": direction_angle,
                    "无人机运动速度(m/s)": speed,
                    "投放时间(s)": t_release[j],
                    "引信延迟(s)": t_delay[j],
                    "投放点x": pos_release[0],
                    "投放点y": pos_release[1],
                    "投放点z": pos_release[2],
                    "起爆点x": pos_detonate[0],
                    "起爆点y": pos_detonate[1],
                    "起爆点z": pos_detonate[2],
                }
            )

    df = pd.DataFrame(results_data)

    # 保存结果
    output_filename = (
        f"result3_collaborative_{datetime.datetime.now().strftime('%H%M%S')}.csv"
    )
    output_path = f"A题/{output_filename}"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n详细结果已保存到: {output_path}")
