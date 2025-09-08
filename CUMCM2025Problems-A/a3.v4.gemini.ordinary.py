import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm
from scipy.optimize import basinhopping, Bounds
import matplotlib.pyplot as plt
import matplotlib

# Set a font that supports Chinese characters
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

Vector3 = NDArray[npy.float64]
Trajectory = List[Vector3]  # or NDArray[npy.float64]

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
from numba.typed import List as NumbaList
from numba.experimental import jitclass

speedFYMin = 70.0
speedFYMax = 140.0
G = 9.8
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0
DT = 0.1  # Time step for simulation

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


@numba.njit()
def getMissilePosition(t: float) -> Vector3:
    return posMissile + speedMissile * t * directionMissile


@numba.njit()
def getCloudPosition(t: float, posDetonate: Vector3, tDetonate: float) -> Vector3:
    return npy.array(
        [posDetonate[0], posDetonate[1], posDetonate[2] - speedCloud * (t - tDetonate)]
    )


@numba.njit()
def distancePoint2Line(
    linePoint1: Vector3, linePoint2: Vector3, targetPoint: Vector3
) -> float:
    lineVec: Vector3 = linePoint2 - linePoint1
    pointVec: Vector3 = targetPoint - linePoint1
    # Handle zero-length lineVec
    dot_lineVec = npy.dot(lineVec, lineVec)
    if dot_lineVec == 0.0:
        return npy.linalg.norm(pointVec)
    s = npy.dot(lineVec, pointVec) / dot_lineVec
    s_clamped = max(0.0, min(s, 1.0))
    closest = linePoint1 + s_clamped * lineVec
    return npy.linalg.norm(targetPoint - closest)


@numba.njit()
def calculate_intersection_with_cylinder(posMissile: Vector3) -> NumbaList:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    norm_v2 = npy.linalg.norm(v2directionMissile)
    pointsIntersection = NumbaList()
    if norm_v2 == 0:
        return pointsIntersection

    directionMissile = v2directionMissile / norm_v2

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]

        pointsIntersection.append(
            npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        )
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部

    return pointsIntersection


@numba.njit()
def calculate_perpendicular_plane_intersection(posMissile: Vector3) -> NumbaList:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    norm_v2 = npy.linalg.norm(v2directionMissile)
    pointsIntersection = NumbaList()
    if norm_v2 == 0:
        return pointsIntersection

    directionMissile = v2directionMissile / norm_v2
    directionPerpendicular = npy.array([-directionMissile[1], directionMissile[0]])

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionPerpendicular[0]
        y = posRealTarget[1] + sign * rRealTarget * directionPerpendicular[1]

        pointsIntersection.append(
            npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        )
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部

    return pointsIntersection


@numba.njit()
def calculateCheckpoints(t: float) -> NumbaList:
    posNowMissile: Vector3 = getMissilePosition(t)
    points = NumbaList()
    points_cylinder = calculate_intersection_with_cylinder(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    points_perp = calculate_perpendicular_plane_intersection(posNowMissile)
    for p in points_perp:
        points.append(p)
    return points


@numba.njit()
def checkSmokeBetween(
    posMissile: Vector3, posCloud: Vector3, posCheckpoint: Vector3
) -> bool:
    return npy.dot(posCloud - posMissile, posCheckpoint - posMissile) > 0


@numba.njit()
def checkCovered(t: float, tDetonate: float, posDetonate: Vector3) -> bool:
    if t < tDetonate or t > tDetonate + tCloud:
        return False
    posNowMissile = getMissilePosition(t)
    checkpoints = calculateCheckpoints(t)
    if len(checkpoints) == 0:  # No checkpoints means no line of sight to target
        return True
    posNowCloud = getCloudPosition(t, posDetonate, tDetonate)

    # If missile is inside the cloud, it's covered
    if npy.linalg.norm(posNowMissile - posNowCloud) <= rCloud:
        return True

    for checkpoint in checkpoints:
        d = distancePoint2Line(posNowMissile, checkpoint, posNowCloud)
        is_between = checkSmokeBetween(posNowMissile, posNowCloud, checkpoint)
        if not (d <= rCloud and is_between):
            return False  # This checkpoint is not covered, so line of sight is clear
    return True  # All checkpoints are covered


@numba.njit()
def calculateCoverTime(
    thetaFY1: float, vFY1: float, tRelease: float, tDelay: float
) -> NumbaList:
    posRelease: Vector3 = posFY1 + vFY1 * tRelease * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    # Check if detonation happens below ground
    if posRelease[2] - 0.5 * G * (tDelay**2) < 0:
        return NumbaList([(0.0, 0.0)])

    posDetonate: Vector3 = posRelease + vFY1 * tDelay * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
    tDetonate = tRelease + tDelay

    t_missile_hit_target = -posMissile[0] / vMissile[0]

    # Simulation time from missile perspective
    iterator = npy.arange(tDetonate, min(tDetonate + tCloud, t_missile_hit_target), DT)

    intervals = NumbaList()
    is_covered = False
    start_cover_time = 0.0

    if len(iterator) == 0:
        return intervals

    for t in iterator:
        currently_covered = checkCovered(t, tDetonate, posDetonate)
        if currently_covered and not is_covered:
            is_covered = True
            start_cover_time = t
        elif not currently_covered and is_covered:
            is_covered = False
            intervals.append((start_cover_time, t))

    if is_covered:
        intervals.append((start_cover_time, iterator[-1]))

    return intervals


def get_union_intervals(
    list_of_intervals: List[List[Tuple[float, float]]],
) -> List[Tuple[float, float]]:
    all_intervals = [
        interval
        for sublist in list_of_intervals
        for interval in sublist
        if interval[1] > interval[0]
    ]
    if not all_intervals:
        return []

    all_intervals.sort(key=lambda x: x[0])

    merged = [all_intervals[0]]
    for current_start, current_end in all_intervals[1:]:
        last_start, last_end = merged[-1]
        if current_start <= last_end:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
    return merged


def calculate_union_cover_time(
    list_of_intervals: List[List[Tuple[float, float]]],
) -> float:
    merged = get_union_intervals(list_of_intervals)
    total_duration = sum(end - start for start, end in merged)
    return total_duration


def greedy_find_best_shots(theta, v, t_release_range, t_delay_range, num_grenades=3):
    best_shots_params = []
    cumulative_intervals = []

    last_t_release = -1.0

    for i in range(num_grenades):
        best_incremental_cover = -1.0
        best_params_for_shot = None
        best_intervals_for_shot = None

        # Define search space for current grenade
        current_t_release_min = last_t_release + 1.0

        for t_release in npy.arange(
            max(t_release_range[0], current_t_release_min), t_release_range[1], 0.5
        ):
            for t_delay in npy.arange(t_delay_range[0], t_delay_range[1], 0.5):

                intervals = calculateCoverTime(theta, v, t_release, t_delay)

                # Convert NumbaList to Python list for union calculation
                py_intervals = [iv for iv in intervals]

                current_union_time = calculate_union_cover_time(
                    cumulative_intervals + [py_intervals]
                )

                if current_union_time > best_incremental_cover:
                    best_incremental_cover = current_union_time
                    best_params_for_shot = (t_release, t_delay)
                    best_intervals_for_shot = py_intervals

        if best_params_for_shot:
            best_shots_params.append(best_params_for_shot)
            cumulative_intervals.append(best_intervals_for_shot)
            last_t_release = best_params_for_shot[0]
        else:
            # Could not find a valid shot
            break

    final_union_time = calculate_union_cover_time(cumulative_intervals)
    return final_union_time, best_shots_params


def objective_3_grenades(params: NDArray[npy.float64]) -> float:
    theta, v = params
    t_release_range = (0, 15)  # Search space for release time
    t_delay_range = (0, 10)  # Search space for delay time

    total_cover_time, _ = greedy_find_best_shots(
        theta, v, t_release_range, t_delay_range
    )

    # We want to maximize cover time, so we minimize its negative
    return -total_cover_time


def plot_cover_intervals(individual_intervals, union_intervals, title):
    fig, ax = plt.subplots(figsize=(15, 5))

    colors = ["#1f77b4", "#2ca02c", "#ff7f0e"]  # Blue, Green, Orange

    # Plot individual grenade intervals
    for i, grenade_intervals in enumerate(individual_intervals):
        for start, end in grenade_intervals:
            ax.broken_barh([(start, end - start)], (i + 1.5, 0.8), facecolors=colors[i])

    # Plot union intervals
    for start, end in union_intervals:
        ax.broken_barh([(start, end - start)], (0.5, 0.8), facecolors="#d62728")  # Red

    ax.set_ylim(0, 4)
    ax.set_xlim(55, 70)  # Adjust based on expected time range of missile flight
    ax.set_xlabel("时间 (s) [导弹发射后]")
    ax.set_ylabel("干扰来源")
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["联合遮蔽", "烟幕弹 1", "烟幕弹 2", "烟幕弹 3"])
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.set_title(title)
    plt.show()


if __name__ == "__main__":
    # Bounds for theta (drone heading) and v (drone speed)
    bounds = Bounds([npy.deg2rad(175), speedFYMin], [npy.deg2rad(185), speedFYMax])

    # Initial guess
    x0 = npy.array([npy.deg2rad(180), 100])

    n_iterations = 100  # Reduced for quicker demonstration, increase for better results
    pbar = tqdm(total=n_iterations, desc="Optimizing 3-Grenade Strategy")

    best_f_value = [float("inf")]

    def progress_callback(x, f, accept):
        if f < best_f_value[0]:
            best_f_value[0] = f
        pbar.update(1)
        pbar.set_postfix(best_total_cover=f"{-best_f_value[0]:.4f}", refresh=True)

    print("Using basinhopping with a greedy strategy for 3 grenades...")
    minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}
    result: OptimizeResult = basinhopping(
        objective_3_grenades,
        x0,
        minimizer_kwargs=minimizer_kwargs,
        niter=n_iterations,
        T=1.0,
        stepsize=0.1,
        callback=progress_callback,
    )
    pbar.close()

    print("\nOptimization Complete!")

    best_params_trajectory = result.x
    best_total_cover = -result.fun
    theta_opt, v_opt = best_params_trajectory

    # Rerun the greedy search with the optimal trajectory to get the final grenade parameters
    _, best_shots = greedy_find_best_shots(theta_opt, v_opt, (0, 15), (0, 10))

    print("\n--- Optimal 3-Grenade Strategy ---")
    print(f"Drone Flight Direction (theta): {npy.rad2deg(theta_opt):.2f}°")
    print(f"Drone Flight Speed (v): {v_opt:.2f} m/s")
    print(f"Maximum Total Cover Time (Union): {best_total_cover:.2f} s")
    print("\nGrenade Deployment Sequence:")
    all_shot_intervals = []
    for i, (t_release, t_delay) in enumerate(best_shots):
        print(f"  Grenade {i+1}:")
        print(f"    Release Time (t_release): {t_release:.2f} s")
        print(f"    Detonation Delay (t_delay): {t_delay:.2f} s")
        intervals = calculateCoverTime(theta_opt, v_opt, t_release, t_delay)
        py_intervals = [iv for iv in intervals]
        all_shot_intervals.append(py_intervals)

    # Calculate union of intervals for plotting
    union_intervals = get_union_intervals(all_shot_intervals)

    # Plot the results
    plot_cover_intervals(
        all_shot_intervals,
        union_intervals,
        f"最优策略下的遮蔽时间区间 (总时长: {best_total_cover:.2f}s)",
    )
