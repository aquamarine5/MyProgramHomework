import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from scipy.optimize import basinhopping, Bounds
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm

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
    return posMissile + t * vMissile


@numba.njit()
def getCloudPosition(t: float, posDetonate: Vector3, tDetonate: float) -> Vector3:
    if t < tDetonate:
        # Before detonation, the cloud doesn't exist in its final form.
        # To avoid issues, we can return a position far away.
        return npy.array([npy.inf, npy.inf, npy.inf])
    return npy.array(
        [posDetonate[0], posDetonate[1], posDetonate[2] - speedCloud * (t - tDetonate)]
    )


@numba.njit()
def distancePoint2Line(
    linePoint1: Vector3, linePoint2: Vector3, targetPoint: Vector3
) -> float:
    lineVec: Vector3 = linePoint2 - linePoint1
    pointVec: Vector3 = targetPoint - linePoint1
    lineVec_norm_sq = npy.dot(lineVec, lineVec)
    if lineVec_norm_sq == 0:
        return npy.linalg.norm(pointVec)
    s = npy.dot(lineVec, pointVec) / lineVec_norm_sq
    s_clamped = max(0.0, min(s, 1.0))
    closest = linePoint1 + s_clamped * lineVec
    return npy.linalg.norm(targetPoint - closest)


@numba.njit()
def calculate_intersection_with_cylinder(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    norm_v2 = npy.linalg.norm(v2directionMissile)
    pointsIntersection = NumbaList()
    if norm_v2 == 0:
        # This case is unlikely but handled for safety.
        pointsIntersection.append(
            npy.array(
                [
                    posRealTarget[0] + rRealTarget,
                    posRealTarget[1],
                    posRealTarget[2] + hRealTarget,
                ]
            )
        )
        pointsIntersection.append(
            npy.array(
                [posRealTarget[0] + rRealTarget, posRealTarget[1], posRealTarget[2]]
            )
        )
        pointsIntersection.append(
            npy.array(
                [
                    posRealTarget[0] - rRealTarget,
                    posRealTarget[1],
                    posRealTarget[2] + hRealTarget,
                ]
            )
        )
        pointsIntersection.append(
            npy.array(
                [posRealTarget[0] - rRealTarget, posRealTarget[1], posRealTarget[2]]
            )
        )
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
def calculate_perpendicular_plane_intersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    norm_v2 = npy.linalg.norm(v2directionMissile)
    pointsIntersection = NumbaList()
    if norm_v2 == 0:
        # This case is unlikely but handled for safety.
        return pointsIntersection  # Return empty Numba list

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
def get6points(t: float) -> List[Vector3]:
    # This function uses a simplified model based on the MATLAB code's structure
    # It defines 4 critical points on the cylinder's silhouette relative to the missile
    posNowMissile = getMissilePosition(t)

    points = NumbaList()

    # Points on the silhouette parallel to the missile's ground projection
    points_cylinder = calculate_intersection_with_cylinder(posNowMissile)
    for p in points_cylinder:
        points.append(p)

    # Points on the silhouette perpendicular to the missile's ground projection
    points_perp = calculate_perpendicular_plane_intersection(posNowMissile)
    for p in points_perp:
        points.append(p)

    return points


@numba.njit()
def checkSmokeBetween(
    posMissile: Vector3, posCloud: Vector3, posCheckpoint: Vector3
) -> bool:
    # Checks if the cloud is between the missile and the checkpoint
    vec_missile_cloud = posCloud - posMissile
    vec_missile_checkpoint = posCheckpoint - posMissile
    # The cloud is "between" if its projection onto the sightline is positive and not beyond the target
    dot_product = npy.dot(vec_missile_cloud, vec_missile_checkpoint)
    return 0 < dot_product < npy.dot(vec_missile_checkpoint, vec_missile_checkpoint)


@numba.njit()
def is_line_segment_obstructed_by_cloud(
    p1: Vector3, p2: Vector3, t: float, t_detonate: float, pos_detonate: Vector3
) -> bool:
    """
    Checks if the line segment p1-p2 is obstructed by a single smoke cloud at time t.
    """
    # 1. Check if the cloud is active
    if not (t_detonate <= t <= t_detonate + tCloud):
        return False

    # 2. Get current cloud position
    pos_cloud_now = getCloudPosition(t, pos_detonate, t_detonate)

    # 3. Check if the line of sight (segment p1-p2) intersects the cloud sphere
    dist = distancePoint2Line(p1, p2, pos_cloud_now)
    if dist > rCloud:
        return False

    # 4. Check if the cloud is positioned between the missile and the target point
    if not checkSmokeBetween(p1, pos_cloud_now, p2):
        return False

    # 5. Check if missile is inside the cloud (special case)
    if npy.linalg.norm(p1 - pos_cloud_now) <= rCloud:
        return True

    return True


@numba.njit()
def calculate_total_shielding_time(params: NDArray[npy.float64]) -> float:
    """
    Calculates the total union shielding time for 3 bombs.
    params: [angle, speed, t_release1, t_delay1, delta_t_release2, t_delay2, delta_t_release3, t_delay3]
    """
    angle, speed, t_r1, t_d1, dt_r2, t_d2, dt_r3, t_d3 = params

    # --- Calculate absolute times and positions for all 3 bombs ---
    v_fy1_dir = npy.array([npy.cos(angle), npy.sin(angle), 0.0])

    # Bomb 1
    t_release1 = t_r1
    t_delay1 = t_d1
    pos_release1 = posFY1 + v_fy1_dir * speed * t_release1
    pos_detonate1 = pos_release1 + v_fy1_dir * speed * t_delay1
    pos_detonate1[2] -= 0.5 * G * t_delay1**2
    t_detonate1 = t_release1 + t_delay1
    if pos_detonate1[2] < 0:
        return 0.0  # Invalid detonation

    # Bomb 2
    t_release2 = t_release1 + dt_r2
    t_delay2 = t_d2
    pos_release2 = posFY1 + v_fy1_dir * speed * t_release2
    pos_detonate2 = pos_release2 + v_fy1_dir * speed * t_delay2
    pos_detonate2[2] -= 0.5 * G * t_delay2**2
    t_detonate2 = t_release2 + t_delay2
    if pos_detonate2[2] < 0:
        return 0.0  # Invalid detonation

    # Bomb 3
    t_release3 = t_release2 + dt_r3
    t_delay3 = t_d3
    pos_release3 = posFY1 + v_fy1_dir * speed * t_release3
    pos_detonate3 = pos_release3 + v_fy1_dir * speed * t_delay3
    pos_detonate3[2] -= 0.5 * G * t_delay3**2
    t_detonate3 = t_release3 + t_delay3
    if pos_detonate3[2] < 0:
        return 0.0  # Invalid detonation

    # --- Simulation to calculate total covered time ---
    total_covered_time = 0.0
    DT = 0.1  # Simulation time step
    t_max_sim = 100.0  # Max simulation time

    time_iterator = npy.arange(0, t_max_sim, DT)

    for t in time_iterator:
        pos_missile_now = getMissilePosition(t)
        key_points = get6points(t)

        if len(key_points) == 0:
            continue

        all_key_points_covered = True
        for kp in key_points:
            is_kp_covered_by_any_cloud = (
                is_line_segment_obstructed_by_cloud(
                    pos_missile_now, kp, t, t_detonate1, pos_detonate1
                )
                or is_line_segment_obstructed_by_cloud(
                    pos_missile_now, kp, t, t_detonate2, pos_detonate2
                )
                or is_line_segment_obstructed_by_cloud(
                    pos_missile_now, kp, t, t_detonate3, pos_detonate3
                )
            )
            if not is_kp_covered_by_any_cloud:
                all_key_points_covered = False
                break

        if all_key_points_covered:
            total_covered_time += DT

    return total_covered_time


def objective_3_bombs(params: NDArray[npy.float64]) -> float:
    """Wrapper for the objective function to be minimized."""
    return -calculate_total_shielding_time(params)


if __name__ == "__main__":
    # Parameter bounds for optimization:
    # [angle, speed, t_release1, t_delay1, delta_t_release2, t_delay2, delta_t_release3, t_delay3]
    # delta_t_release must be >= 1 second
    bounds = Bounds(
        [npy.deg2rad(170), speedFYMin, 0.0, 0.1, 1.0, 0.1, 1.0, 0.1],
        [npy.deg2rad(190), speedFYMax, 10.0, 5.0, 10.0, 5.0, 10.0, 5.0],
    )

    # Initial guess
    x0 = npy.array([npy.deg2rad(180), 100, 2, 2, 3, 2, 3, 2])

    n_iterations = (
        200  # Adjust as needed, more iterations = longer runtime but better results
    )
    pbar = tqdm(total=n_iterations, desc="Optimizing 3-Bomb Strategy")

    best_f_value = [float("inf")]

    def progress_callback(x, f, accept):
        if f < best_f_value[0]:
            best_f_value[0] = f
        pbar.update(1)
        pbar.set_postfix(max_tCover=f"{-best_f_value[0]:.4f}", refresh=True)

    print("Running basinhopping for global optimization...")
    minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}
    result: OptimizeResult = basinhopping(
        objective_3_bombs,
        x0,
        minimizer_kwargs=minimizer_kwargs,
        niter=n_iterations,
        T=1.0,
        stepsize=0.5,
        callback=progress_callback,
    )
    pbar.close()

    print("\nOptimization Complete!")

    best_params = result.x
    max_cover_time = -result.fun

    (
        angle_opt,
        speed_opt,
        t_r1_opt,
        t_d1_opt,
        dt_r2_opt,
        t_d2_opt,
        dt_r3_opt,
        t_d3_opt,
    ) = best_params

    # --- Recalculate and display detailed results ---
    v_fy1_dir_opt = npy.array([npy.cos(angle_opt), npy.sin(angle_opt), 0.0])

    # Bomb 1
    t_release1 = t_r1_opt
    t_delay1 = t_d1_opt
    pos_release1 = posFY1 + v_fy1_dir_opt * speed_opt * t_release1
    pos_detonate1 = pos_release1 + v_fy1_dir_opt * speed_opt * t_delay1
    pos_detonate1[2] -= 0.5 * G * t_delay1**2
    t_detonate1 = t_release1 + t_delay1

    # Bomb 2
    t_release2 = t_release1 + dt_r2_opt
    t_delay2 = t_d2_opt
    pos_release2 = posFY1 + v_fy1_dir_opt * speed_opt * t_release2
    pos_detonate2 = pos_release2 + v_fy1_dir_opt * speed_opt * t_delay2
    pos_detonate2[2] -= 0.5 * G * t_delay2**2
    t_detonate2 = t_release2 + t_delay2

    # Bomb 3
    t_release3 = t_release2 + dt_r3_opt
    t_delay3 = t_d3_opt
    pos_release3 = posFY1 + v_fy1_dir_opt * speed_opt * t_release3
    pos_detonate3 = pos_release3 + v_fy1_dir_opt * speed_opt * t_delay3
    pos_detonate3[2] -= 0.5 * G * t_delay3**2
    t_detonate3 = t_release3 + t_delay3

    print("\n--- Optimal 3-Bomb Strategy ---")
    print(f"Max. Total Shielding Time: {max_cover_time:.4f} s")
    print("\n--- UAV Flight Plan ---")
    print(f"Flight Direction (theta): {npy.rad2deg(angle_opt):.4f}°")
    print(f"Flight Speed (v): {speed_opt:.4f} m/s")

    print("\n--- Bomb 1 Details ---")
    print(f"Release Time: {t_release1:.4f} s")
    print(f"Delay Time:   {t_delay1:.4f} s")
    print(f"Detonation Time: {t_detonate1:.4f} s")
    print(f"Release Position: {pos_release1}")
    print(f"Detonation Position: {pos_detonate1}")

    print("\n--- Bomb 2 Details ---")
    print(f"Release Time: {t_release2:.4f} s (Delta: {dt_r2_opt:.4f} s)")
    print(f"Delay Time:   {t_delay2:.4f} s")
    print(f"Detonation Time: {t_detonate2:.4f} s")
    print(f"Release Position: {pos_release2}")
    print(f"Detonation Position: {pos_detonate2}")

    print("\n--- Bomb 3 Details ---")
    print(f"Release Time: {t_release3:.4f} s (Delta: {dt_r3_opt:.4f} s)")
    print(f"Delay Time:   {t_delay3:.4f} s")
    print(f"Detonation Time: {t_detonate3:.4f} s")
    print(f"Release Position: {pos_release3}")
    print(f"Detonation Position: {pos_detonate3}")
