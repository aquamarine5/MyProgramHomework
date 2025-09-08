import datetime
import sys
from time import time
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Optional, Tuple
import pandas as pd

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination

# ================== 初始化参数 (与v1版本相同) ==================
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


# ================== 核心计算函数 (与v1版本相同, Numba JIT) ==================
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


@numba.njit(cache=True)
def evaluate_single_uav_multi_objective(
    params: NDArray,
    uav_idx: int,
) -> NDArray:
    """
    评估单个无人机策略，返回对三个导弹各自的遮蔽时间 (负数)
    params: [direction_angle, speed, t_release1, t_span12, t_span23, t_delay1, t_delay2, t_delay3]
    """
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
    t_detonate = t_release + t_delay

    direction_uav = npy.array([npy.cos(direction_angle), npy.sin(direction_angle), 0.0])
    v_uav = speed * direction_uav

    pos_detonate = npy.zeros((3, 3))
    for i in range(3):
        pos_release_i = pos_UAVs_0[uav_idx] + v_uav * t_release[i]
        pos_detonate[i] = (
            pos_release_i
            + v_uav * t_delay[i]
            - 0.5 * G * t_delay[i] ** 2 * npy.array([0.0, 0.0, 1.0])
        )

    missile_masked_times = npy.zeros(3)

    for m_idx in range(len(pos_missiles_0)):
        is_masked_list = npy.zeros(len(t_calculate_range), dtype=npy.bool_)
        for t_idx, t_now in enumerate(t_calculate_range):
            pos_missile_now = get_missile_position(t_now, m_idx)
            active_clouds = []
            for i in range(3):
                if t_detonate[i] <= t_now <= t_detonate[i] + cloud_lifetime:
                    active_clouds.append(
                        get_cloud_position(t_now, pos_detonate[i], t_detonate[i])
                    )
            if not active_clouds:
                continue
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
        missile_masked_times[m_idx] = npy.sum(is_masked_list) * DT

    return -missile_masked_times  # Pymoo默认最小化，所以返回负数


# ================== Pymoo 问题定义 ==================
class UAVOptimizationProblem(Problem):
    def __init__(self, uav_idx, xl, xu):
        super().__init__(n_var=8, n_obj=3, n_constr=0, xl=xl, xu=xu)
        self.uav_idx = uav_idx

    def _evaluate(self, x, out, *args, **kwargs):
        # Pymoo期望 (n_samples, n_objectives)
        results = npy.array(
            [evaluate_single_uav_multi_objective(ind, self.uav_idx) for ind in x]
        )
        out["F"] = results


# ================== 主优化流程 ==================
if __name__ == "__main__":
    num_uavs = 5
    all_uav_best_params = []
    all_uav_contributions = []

    vars_per_uav = 8
    lb = [0, speed_FY_min, 0, min_interval, min_interval, 0.5, 0.5, 0.5]
    ub = [2 * npy.pi, speed_FY_max, 60, 20, 20, 10, 10, 10]

    # NSGA-II 算法
    algorithm = NSGA2(pop_size=100)
    termination = get_termination("n_gen", 40)

    for i in range(num_uavs):
        print(f"\n======== 开始优化无人机 FY{i+1} (NSGA-II) ========")

        problem = UAVOptimizationProblem(uav_idx=i, xl=lb, xu=ub)

        res = minimize(
            problem, algorithm, termination, seed=1, save_history=True, verbose=True
        )

        print(f"无人机 FY{i+1} 优化完成。")

        # 从帕累托前沿中选择一个解
        # 策略：选择总遮蔽时间最长的解
        F = res.F  # (n_solutions, n_objectives)
        X = res.X  # (n_solutions, n_variables)

        total_times = -npy.sum(F, axis=1)  # 计算每个解的总时间
        best_idx = npy.argmax(total_times)  # 找到总时间最长的索引

        best_params = X[best_idx]
        best_objectives = -F[best_idx]  # 转换回正数

        all_uav_best_params.append(best_params)
        all_uav_contributions.append(best_objectives)

        print(f"  - 选定的最优参数: {npy.round(best_params, 2)}")
        print(f"  - 对M1, M2, M3的贡献时间: {npy.round(best_objectives, 2)} s")
        print(f"  - 总贡献时间: {npy.sum(best_objectives):.2f} s")

    # ================== 结果汇总与保存 ==================
    print("\n======== 所有无人机独立优化完成，开始汇总结果 ========")

    results_data = []
    for i, params in enumerate(all_uav_best_params):
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
    output_filename = f"result3_nsga2_{datetime.datetime.now().strftime('%H%M%S')}.csv"
    output_path = f"A题/{output_filename}"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n详细结果已保存到: {output_path}")
