import numpy as np
import time
import numba

# --- 物理模型参数 (与问题1一致) ---
g = 9.8
missile_pos0 = np.array([20000.0, 0.0, 2000.0])
missile_speed = 300.0
missile_target = np.array([0.0, 0.0, 0.0])
missile_dir = (missile_target - missile_pos0) / np.linalg.norm(
    missile_target - missile_pos0
)
true_target = np.array([0.0, 200.0, 0.0])
uav_pos0 = np.array([17800.0, 0.0, 1800.0])
cloud_radius = 10.0
cloud_sink_speed = 3.0
cloud_valid_time = 20.0


# --- 使用Numba JIT加速的物理模型计算函数 ---
@numba.jit(nopython=True)
def missile_position_numba(t, missile_pos0, missile_speed, missile_dir):
    return missile_pos0 + missile_speed * t * missile_dir


@numba.jit(nopython=True)
def line_point_distance_numba(p1, p2, c):
    v = p2 - p1
    w = c - p1
    s = np.dot(v, w) / np.dot(v, v)

    # Numba兼容的clip
    if s < 0.0:
        s_clamped = 0.0
    elif s > 1.0:
        s_clamped = 1.0
    else:
        s_clamped = s

    closest_point_on_segment = p1 + s_clamped * v
    return np.linalg.norm(c - closest_point_on_segment)


@numba.njit()
def calculate_coverage_time_numba(
    uav_speed,
    uav_dir,
    t_release,
    t_delay,
    uav_pos0,
    g,
    missile_pos0,
    missile_speed,
    missile_dir,
    true_target,
    cloud_radius,
    cloud_sink_speed,
    cloud_valid_time,
):
    """
    核心计算函数：根据给定的策略，计算总遮蔽时长 (Numba加速版)
    """
    # 1. 干扰弹投放位置
    release_pos = uav_pos0 + uav_speed * t_release * uav_dir

    # 2. 干扰弹投放时的初速度
    bomb_initial_velocity = uav_speed * uav_dir

    # 3. 计算起爆点位置 (平抛运动)
    detonate_pos = np.array(
        [
            release_pos[0] + bomb_initial_velocity[0] * t_delay,
            release_pos[1] + bomb_initial_velocity[1] * t_delay,
            release_pos[2] - 0.5 * g * (t_delay**2),
        ]
    )

    # 4. 模拟计算遮蔽时长
    t_detonate = t_release + t_delay
    total_covered_time = 0.0
    dt = 0.001  # 时间步长

    start_time = t_detonate
    end_time = t_detonate + cloud_valid_time

    # Numba擅长加速这种循环
    t = start_time
    while t < end_time:
        mpos = missile_position_numba(t, missile_pos0, missile_speed, missile_dir)

        # 烟云中心位置
        cpos = np.array(
            [
                detonate_pos[0],
                detonate_pos[1],
                detonate_pos[2] - cloud_sink_speed * (t - t_detonate),
            ]
        )

        d = line_point_distance_numba(mpos, true_target, cpos)
        if d <= cloud_radius:
            total_covered_time += dt
        t += dt

    return total_covered_time


# --- 优化过程 ---
if __name__ == "__main__":
    print("开始进行问题2的优化计算 (Numba加速)...")
    # 首次调用JIT函数时，Numba会进行编译，可能耗时稍长
    print("首次运行Numba编译...")
    calculate_coverage_time_numba(
        70,
        np.array([1.0, 0, 0]),
        1.0,
        2.0,
        uav_pos0,
        g,
        missile_pos0,
        missile_speed,
        missile_dir,
        true_target,
        cloud_radius,
        cloud_sink_speed,
        cloud_valid_time,
    )
    print("编译完成，开始搜索。")

    start_opt_time = time.time()
    MORE_SIZE = 5
    # 离散化决策变量
    uav_speeds = np.linspace(70.0, 140.0, MORE_SIZE * 4)  # 速度: 70, 80, ..., 140
    uav_angles = np.linspace(
        np.deg2rad(175), np.deg2rad(178), MORE_SIZE * 6
    )  # 方向: 175, 176, ..., 178 度
    release_times = np.linspace(2.0, 3.5, MORE_SIZE * 8)  # 投放时间: 2.0, 2.5, ..., 3.5
    delay_times = np.linspace(0.0, 1.0, 5)  # 起爆延迟: 0.0, 0.5, 1.0

    # 初始化最优解记录
    best_coverage = -1.0
    best_params = {}

    total_iterations = (
        len(uav_speeds) * len(uav_angles) * len(release_times) * len(delay_times)
    )
    current_iteration = 0

    # 网格搜索
    for speed in uav_speeds:
        for angle_deg in uav_angles:
            angle_rad = np.deg2rad(angle_deg)
            direction = np.array([np.cos(angle_rad), np.sin(angle_rad), 0])
            for t_rel in release_times:
                for t_del in delay_times:
                    current_iteration += 1
                    if current_iteration % 500 == 0:
                        print(
                            f"  进度: {current_iteration}/{total_iterations} ({100*current_iteration/total_iterations:.1f}%)"
                        )

                    coverage = calculate_coverage_time_numba(
                        speed,
                        direction,
                        t_rel,
                        t_del,
                        uav_pos0,
                        g,
                        missile_pos0,
                        missile_speed,
                        missile_dir,
                        true_target,
                        cloud_radius,
                        cloud_sink_speed,
                        cloud_valid_time,
                    )

                    if coverage > best_coverage:
                        best_coverage = coverage
                        best_params = {
                            "speed": speed,
                            "angle_deg": angle_deg,
                            "t_release": t_rel,
                            "t_delay": t_del,
                        }

    end_opt_time = time.time()
    print(f"\n优化计算完成，耗时: {end_opt_time - start_opt_time:.2f} 秒")

    # --- 输出最优策略 ---
    print("\n--- 最优投放策略 ---")
    print(f"最大有效遮蔽时长: {best_coverage:.2f} 秒")
    print("\n决策变量:")
    print(f"  - 无人机飞行速度: {best_params['speed']} m/s")
    print(f"  - 无人机飞行方向: {best_params['angle_deg']} 度")
    print(f"  - 烟幕弹投放时间: {best_params['t_release']:.1f} 秒")
    print(f"  - 烟幕弹起爆延迟: {best_params['t_delay']:.1f} 秒")

    # 根据最优参数计算投放点和起爆点
    opt_speed = best_params["speed"]
    opt_angle_rad = np.deg2rad(best_params["angle_deg"])
    opt_dir = np.array([np.cos(opt_angle_rad), np.sin(opt_angle_rad), 0])
    opt_t_release = best_params["t_release"]
    opt_t_delay = best_params["t_delay"]

    opt_release_pos = uav_pos0 + opt_speed * opt_t_release * opt_dir
    opt_bomb_vel = opt_speed * opt_dir
    opt_detonate_pos = np.array(
        [
            opt_release_pos[0] + opt_bomb_vel[0] * opt_t_delay,
            opt_release_pos[1] + opt_bomb_vel[1] * opt_t_delay,
            opt_release_pos[2] - 0.5 * g * (opt_t_delay**2),
        ]
    )

    print("\n计算结果:")
    print(
        f"  - 烟幕弹投放点: ({opt_release_pos[0]:.2f}, {opt_release_pos[1]:.2f}, {opt_release_pos[2]:.2f})"
    )
    print(
        f"  - 烟幕弹起爆点: ({opt_detonate_pos[0]:.2f}, {opt_detonate_pos[1]:.2f}, {opt_detonate_pos[2]:.2f})"
    )
