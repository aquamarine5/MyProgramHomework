import datetime
import sys
from time import time
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Optional, Tuple, Dict
from tqdm import tqdm
import pandas as pd

# ==================================
# 场景参数定义 (Scene Parameters)
# ==================================
Vector3 = NDArray[npy.float64]

# --- 导弹定义 (Missile Definitions) ---
posMissiles_0: NDArray[npy.float64] = npy.array(
    [
        [20000.0, 0.0, 2000.0],  # M1
        [19000.0, 600.0, 2100.0],  # M2
        [18000.0, -600.0, 1900.0],  # M3
    ]
)
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])  # 假目标
directionsMissile: NDArray[npy.float64] = npy.array(
    [
        (posMissileTarget - pos) / npy.linalg.norm(posMissileTarget - pos)
        for pos in posMissiles_0
    ]
)

# --- 真实目标定义 (Real Target Definition) ---
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
rRealTarget = 7.0
hRealTarget = 10.0

# --- 无人机定义 (UAV Definitions) ---
posUAVs_0: Dict[str, Vector3] = {
    "FY1": npy.array([17800.0, 0.0, 1800.0]),
    "FY2": npy.array([12000.0, 1400.0, 1400.0]),
    "FY3": npy.array([6000.0, -3000.0, 700.0]),
    "FY4": npy.array([11000.0, 2000.0, 1800.0]),
    "FY5": npy.array([13000.0, -2000.0, 1300.0]),
}
speedFYMin = 70.0
speedFYMax = 140.0
maxFlaresPerUAV = 3
minFlareInterval = 1.0

# --- 烟幕云团物理属性 (Smoke Cloud Physics) ---
G = 9.8
rCloud = 10.0
speedCloudSink = 3.0
tCloudEffective = 20.0

# --- 仿真参数 (Simulation Parameters) ---
DT = 0.02  # 时间步长
RANGE = 50
tCalculateRange = npy.arange(0.0, 100.0, DT, dtype=npy.float32)
nTimeSteps = len(tCalculateRange)

# ==================================
# 核心计算函数 (Core Calculation Functions)
# ==================================


@numba.njit
def getMissilePosition(t: float, missile_idx: int) -> Vector3:
    """计算指定导弹在时刻t的位置"""
    return (
        posMissiles_0[missile_idx] + speedMissile * t * directionsMissile[missile_idx]
    )


@numba.njit
def getCloudPosition(t: float, posDetonate: Vector3, tDetonate: float) -> Vector3:
    """计算烟幕云团在时刻t的位置"""
    return npy.array(
        [
            posDetonate[0],
            posDetonate[1],
            posDetonate[2] - speedCloudSink * (t - tDetonate),
        ]
    )


@numba.njit
def distancePoint2Line(p1: Vector3, p2: Vector3, p0: Vector3) -> float:
    """计算点p0到线段p1-p2的最短距离"""
    lineVec = p2 - p1
    pointVec = p0 - p1
    lineLenSq = npy.dot(lineVec, lineVec)
    if lineLenSq == 0:
        return npy.linalg.norm(p0 - p1)
    s = npy.dot(lineVec, pointVec) / lineLenSq
    s_clamped = max(0.0, min(s, 1.0))
    closest = p1 + s_clamped * lineVec
    return npy.linalg.norm(p0 - closest)


@numba.njit
def checkLineIntersectSphere(
    p1: Vector3, p2: Vector3, center: Vector3, radius: float
) -> bool:
    """检查线段p1-p2是否与球体相交"""
    return distancePoint2Line(p1, p2, center) <= radius


@numba.njit
def get_key_points(n_angle: int, n_height: int) -> NDArray:
    """生成真实目标的圆柱体关键点"""
    points = npy.zeros(((n_angle * n_height), 3), dtype=npy.float64)
    angles = npy.linspace(0, 2 * npy.pi, n_angle)
    heights = npy.linspace(0, hRealTarget, n_height)
    idx = 0
    for h in heights:
        for ang in angles:
            points[idx, 0] = posRealTarget[0] + rRealTarget * npy.cos(ang)
            points[idx, 1] = posRealTarget[1] + rRealTarget * npy.sin(ang)
            points[idx, 2] = posRealTarget[2] + h
            idx += 1
    return points


keyPointsTarget = get_key_points(8, 4)  # 8个角度, 4个高度层


@numba.njit
def calculate_single_flare_shielding(
    pos_uav_0: Vector3,
    angle_deg: float,
    speed: float,
    t_release: float,
    t_delay: float,
) -> NDArray[npy.bool_]:
    """计算单个烟幕弹对所有导弹在所有时间步的遮蔽状态"""
    angle = angle_deg * npy.pi / 180.0  # Convert degrees to radians
    direction_fy = npy.array([npy.cos(angle), npy.sin(angle), 0.0])
    pos_release = pos_uav_0 + speed * t_release * direction_fy
    v_release = speed * direction_fy
    pos_detonate = (
        pos_release
        + v_release * t_delay
        - 0.5 * G * t_delay**2 * npy.array([0.0, 0.0, 1.0])
    )
    t_detonate = t_release + t_delay

    # (n_missiles, n_timesteps)
    shielding_matrix = npy.zeros((len(posMissiles_0), nTimeSteps), dtype=npy.bool_)

    t_shield_start = t_detonate
    t_shield_end = t_detonate + tCloudEffective

    for i_t, t_now in enumerate(tCalculateRange):
        if not (t_shield_start <= t_now <= t_shield_end):
            continue

        pos_cloud_now = getCloudPosition(t_now, pos_detonate, t_detonate)

        for i_m in range(len(posMissiles_0)):
            pos_missile_now = getMissilePosition(t_now, i_m)

            is_fully_covered = True
            for kp in keyPointsTarget:
                if not checkLineIntersectSphere(
                    pos_missile_now, kp, pos_cloud_now, rCloud
                ):
                    is_fully_covered = False
                    break

            if is_fully_covered:
                shielding_matrix[i_m, i_t] = True

    return shielding_matrix


# ==================================
# 贪心算法实现 (Greedy Algorithm Implementation)
# ==================================


def generate_candidates(uav_id: str, pos_uav_0: Vector3) -> List[Dict]:
    """为单个无人机生成候选投放方案"""
    candidates = []

    # 稀疏网格搜索
    angles_deg = npy.linspace(0, 360, 12)  # 12个航向 (0-360度)
    speeds = npy.linspace(speedFYMin, speedFYMax, RANGE)  # 3个速度档位
    t_releases = npy.linspace(1.0, 60.0, RANGE)  # 15个投放时间
    t_delays = npy.linspace(0.5, 15.0, RANGE)  # 10个引信延迟

    pbar = tqdm(
        total=len(angles_deg) * len(speeds) * len(t_releases) * len(t_delays),
        desc=f"生成{uav_id}候选",
        leave=False,
    )

    for angle_deg in angles_deg:
        for speed in speeds:
            for t_release in t_releases:
                for t_delay in t_delays:
                    shielding_matrix = calculate_single_flare_shielding(
                        pos_uav_0, angle_deg, speed, t_release, t_delay
                    )
                    if npy.any(shielding_matrix):
                        candidates.append(
                            {
                                "uav_id": uav_id,
                                "angle_deg": angle_deg,
                                "speed": speed,
                                "t_release": t_release,
                                "t_delay": t_delay,
                                "shielding_matrix": shielding_matrix,
                            }
                        )
                    pbar.update(1)
    pbar.close()
    return candidates


def run_greedy_solver():
    """执行贪心算法求解"""
    print("1. 正在为所有无人机生成候选投放方案...")
    all_candidates = {}
    for uav_id, pos_uav_0 in posUAVs_0.items():
        all_candidates[uav_id] = generate_candidates(uav_id, pos_uav_0)
        print(f"  - {uav_id} 生成了 {len(all_candidates[uav_id])} 个有效候选。")

    # --- 初始化状态 ---
    final_plan = []
    total_flares = sum(maxFlaresPerUAV for _ in posUAVs_0)

    # (n_missiles, n_timesteps)
    union_shielding = npy.zeros((len(posMissiles_0), nTimeSteps), dtype=npy.bool_)

    uav_locks = {
        uav_id: {
            "locked": False,
            "angle_deg": None,
            "speed": None,
            "flares_deployed": 0,
            "release_times": [],
        }
        for uav_id in posUAVs_0
    }

    print("\n2. 开始贪心增量选择...")
    pbar_main = tqdm(total=total_flares, desc="选择烟幕弹")

    for i_flare in range(total_flares):
        best_candidate = None
        max_marginal_gain = -1.0

        for uav_id, candidates in all_candidates.items():
            uav_state = uav_locks[uav_id]

            # 检查约束
            if uav_state["flares_deployed"] >= maxFlaresPerUAV:
                continue

            for cand in candidates:
                # 如果无人机已锁定，则只考虑匹配的候选
                if uav_state["locked"]:
                    if not (
                        npy.isclose(cand["angle_deg"], uav_state["angle_deg"])
                        and npy.isclose(cand["speed"], uav_state["speed"])
                    ):
                        continue

                # 检查最小投放间隔
                is_too_close = False
                for deployed_t in uav_state["release_times"]:
                    if abs(cand["t_release"] - deployed_t) < minFlareInterval:
                        is_too_close = True
                        break
                if is_too_close:
                    continue

                # 计算边际收益
                current_total_shielded_time = npy.sum(union_shielding) * DT

                # 计算加入此候选后的新并集
                new_union = union_shielding | cand["shielding_matrix"]
                new_total_shielded_time = npy.sum(new_union) * DT

                marginal_gain = new_total_shielded_time - current_total_shielded_time

                if marginal_gain > max_marginal_gain:
                    max_marginal_gain = marginal_gain
                    best_candidate = cand

        if best_candidate is None or max_marginal_gain < DT:  # 如果没有收益或收益太小
            print(f"\n在第 {i_flare + 1} 枚弹时，无明显收益，提前终止。")
            break

        # --- 更新状态 ---
        final_plan.append(best_candidate)
        union_shielding |= best_candidate["shielding_matrix"]

        uav_id = best_candidate["uav_id"]
        uav_state = uav_locks[uav_id]

        uav_state["flares_deployed"] += 1
        uav_state["release_times"].append(best_candidate["t_release"])

        if not uav_state["locked"]:
            uav_state["locked"] = True
            uav_state["angle_deg"] = best_candidate["angle_deg"]
            uav_state["speed"] = best_candidate["speed"]

        pbar_main.update(1)
        pbar_main.set_postfix({"新增时长": f"{max_marginal_gain:.2f}s"})

    pbar_main.close()
    return final_plan, union_shielding


# ==================================
# 结果处理与输出 (Result Processing and Output)
# ==================================
def process_and_save_results(final_plan, union_shielding):
    """处理并保存最终结果"""
    print("\n3. 正在处理并保存结果...")
    if not final_plan:
        print("未找到可行的投放计划。")
        return

    results_data = []
    for flare_info in final_plan:
        uav_id = flare_info["uav_id"]
        pos_uav_0 = posUAVs_0[uav_id]
        angle_deg = flare_info["angle_deg"]
        speed = flare_info["speed"]
        t_release = flare_info["t_release"]
        t_delay = flare_info["t_delay"]

        angle = npy.deg2rad(angle_deg)
        direction_fy = npy.array([npy.cos(angle), npy.sin(angle), 0.0])
        pos_release = pos_uav_0 + speed * t_release * direction_fy
        v_release = speed * direction_fy
        pos_detonate = (
            pos_release
            + v_release * t_delay
            - 0.5 * G * t_delay**2 * npy.array([0.0, 0.0, 1.0])
        )

        # 单独计算此弹的贡献时长
        individual_shield_time = npy.sum(flare_info["shielding_matrix"]) * DT

        results_data.append(
            {
                "无人机编号": uav_id,
                "无人机运动方向 (deg)": angle_deg,
                "无人机运动速度 (m/s)": speed,
                "烟幕弹投放时刻 (s)": t_release,
                "烟幕弹引信延迟 (s)": t_delay,
                "投放点x": pos_release[0],
                "投放点y": pos_release[1],
                "投放点z": pos_release[2],
                "起爆点x": pos_detonate[0],
                "起爆点y": pos_detonate[1],
                "起爆点z": pos_detonate[2],
                "单弹贡献总时长 (s)": individual_shield_time,
            }
        )

    df = pd.DataFrame(results_data)

    # 排序和重新编号
    df = df.sort_values(by=["无人机编号", "烟幕弹投放时刻 (s)"]).reset_index(drop=True)
    df.insert(0, "烟幕弹总编号", df.index + 1)

    timestamp = datetime.datetime.now().strftime("%H%M%S")
    output_path = (
        f"d:/ProgramSource/CUMCM2025Problems/A题/result5_greedy_{timestamp}.csv"
    )
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"  - 详细投放计划已保存到: {output_path}")

    # 计算最终总遮蔽时长
    total_shielded_time = npy.sum(union_shielding) * DT
    missile1_time = npy.sum(union_shielding[0, :]) * DT
    missile2_time = npy.sum(union_shielding[1, :]) * DT
    missile3_time = npy.sum(union_shielding[2, :]) * DT

    print("\n--- 最终结果 ---")
    print(f"总计投放 {len(final_plan)} 枚烟幕弹。")
    print(f"导弹M1有效遮蔽时间: {missile1_time:.2f} s")
    print(f"导弹M2有效遮蔽时间: {missile2_time:.2f} s")
    print(f"导弹M3有效遮蔽时间: {missile3_time:.2f} s")
    print(f"所有导弹遮蔽时间总和: {total_shielded_time:.2f} s")


if __name__ == "__main__":
    start_time = time()
    final_plan, final_shielding = run_greedy_solver()
    process_and_save_results(final_plan, final_shielding)
    end_time = time()
    print(f"\n总耗时: {end_time - start_time:.2f} 秒")
