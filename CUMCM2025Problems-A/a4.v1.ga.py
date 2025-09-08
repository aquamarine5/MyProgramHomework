import numpy as np
from sko.GA import GA
import numba
from tqdm import tqdm

# ================== Constants and Initial Positions ==================
# Based on problem4_1.m and a3.v9.handwritten.final.py

# --- Basic Parameters ---
G = 9.8  # Gravitational acceleration, m/s^2
V_M1 = 300.0  # Missile M1 speed, m/s
R_CLOUD = 10.0  # Smoke cloud radius, m
V_SINK = 3.0  # Smoke cloud sink speed, m/s
CLOUD_LIFETIME = 20.0  # Smoke effective time, s
CYLINDER_RADIUS = 7.0  # True target cylinder radius, m
CYLINDER_HEIGHT = 10.0  # True target cylinder height, m

# --- Initial Positions ---
R_M1_0 = np.array([20000.0, 0.0, 2000.0])  # Missile M1 initial position
O_TARGET = np.array([0.0, 0.0, 0.0])  # Decoy target position (origin)
T_BASE = np.array([0.0, 200.0, 0.0])  # True target base center position

# --- UAV Initial Positions ---
R_FY1_0 = np.array([17800.0, 0.0, 1800.0])
R_FY2_0 = np.array([12000.0, 1400.0, 1400.0])
R_FY3_0 = np.array([6000.0, -3000.0, 700.0])
UAV_POSITIONS = [R_FY1_0, R_FY2_0, R_FY3_0]

# --- Missile Flight Direction ---
E_M1 = (O_TARGET - R_M1_0) / np.linalg.norm(O_TARGET - R_M1_0)

# --- Time Settings ---
DT = 0.05  # Time step for simulation
T_RANGE = np.arange(0, 100, DT)

# ================== Helper Functions (from a3.v9.handwritten.final.py) ==================


@numba.njit(cache=True)
def getMissilePosition(t: float) -> np.ndarray:
    """Calculates missile position at time t."""
    return R_M1_0 + V_M1 * t * E_M1


@numba.njit(cache=True)
def getCloudPosition(
    t: float, pos_detonate: np.ndarray, t_detonate: float
) -> np.ndarray:
    """Calculates smoke cloud center position at time t."""
    if t < t_detonate:
        return np.array([np.inf, np.inf, np.inf])  # Does not exist yet
    return np.array(
        [pos_detonate[0], pos_detonate[1], pos_detonate[2] - V_SINK * (t - t_detonate)]
    )


@numba.njit(cache=True)
def distancePoint2Line(
    line_point1: np.ndarray, line_point2: np.ndarray, target_point: np.ndarray
) -> float:
    """Calculates the minimum distance from a point to a line segment."""
    line_vec = line_point2 - line_point1
    point_vec = target_point - line_point1
    s = np.dot(line_vec, point_vec) / np.dot(line_vec, line_vec)
    s_clamped = max(0.0, min(s, 1.0))
    closest = line_point1 + s_clamped * line_vec
    return np.linalg.norm(target_point - closest)


@numba.njit(cache=True)
def checkLineIntersectSphere(
    line_point1: np.ndarray,
    line_point2: np.ndarray,
    sphere_center: np.ndarray,
    sphere_radius: float,
) -> bool:
    """Checks if a line segment intersects with a sphere."""
    # Quick check if endpoints are inside
    if np.linalg.norm(line_point1 - sphere_center) <= sphere_radius:
        return True
    if np.linalg.norm(line_point2 - sphere_center) <= sphere_radius:
        return True
    return distancePoint2Line(line_point1, line_point2, sphere_center) <= sphere_radius


@numba.njit(cache=True)
def get_key_points():
    """Generates 6 key points on the target cylinder."""
    n_points = 2
    key_points = np.zeros((2 * n_points + 2, 3))
    # Base and top centers
    key_points[0, :] = T_BASE
    key_points[1, :] = T_BASE + np.array([0, 0, CYLINDER_HEIGHT])
    # Points on base circle
    for i in range(n_points):
        ang = 2 * np.pi * i / n_points
        key_points[2 + i, :] = T_BASE + CYLINDER_RADIUS * np.array(
            [np.cos(ang), np.sin(ang), 0]
        )
    # Points on top circle
    for i in range(n_points):
        ang = 2 * np.pi * i / n_points
        key_points[2 + n_points + i, :] = (
            T_BASE
            + CYLINDER_RADIUS * np.array([np.cos(ang), np.sin(ang), 0])
            + np.array([0, 0, CYLINDER_HEIGHT])
        )
    return key_points


KEY_POINTS = get_key_points()

# ================== Core Logic for GA Fitness Calculation ==================


def calculate_shielding_time(theta: np.ndarray) -> float:
    """
    Calculates the total effective shielding time for a given set of UAV strategies.
    This is the fitness function for the GA.
    theta: 1D array of 12 parameters [angle1, speed1, release1, delay1, angle2, ...]
    """
    t_explosions = np.zeros(3)
    pos_explosions = np.zeros((3, 3))

    for i in range(3):
        angle, speed, t_release, t_delay = (
            theta[i * 4],
            theta[i * 4 + 1],
            theta[i * 4 + 2],
            theta[i * 4 + 3],
        )

        t_explosion = t_release + t_delay
        e_fy = np.array([np.cos(angle), np.sin(angle), 0.0])

        r_fy_release = UAV_POSITIONS[i] + speed * t_release * e_fy
        r_s_explosion = (
            r_fy_release
            + t_delay * speed * e_fy
            - 0.5 * G * t_delay**2 * np.array([0.0, 0.0, 1.0])
        )

        t_explosions[i] = t_explosion
        pos_explosions[i, :] = r_s_explosion

    total_effective_time = 0.0

    for t in T_RANGE:
        r_m1_t = getMissilePosition(t)

        # Determine which clouds are active
        active_clouds_indices = []
        for i in range(3):
            if t_explosions[i] <= t <= t_explosions[i] + CLOUD_LIFETIME:
                active_clouds_indices.append(i)

        if not active_clouds_indices:
            continue

        # Get positions of active clouds
        cloud_positions = np.zeros((len(active_clouds_indices), 3))
        for idx, cloud_idx in enumerate(active_clouds_indices):
            cloud_positions[idx, :] = getCloudPosition(
                t, pos_explosions[cloud_idx], t_explosions[cloud_idx]
            )

        # Check if all key points are shielded
        all_points_shielded = True
        for kp in KEY_POINTS:
            point_is_shielded = False
            for cp in cloud_positions:
                if checkLineIntersectSphere(r_m1_t, kp, cp, R_CLOUD):
                    point_is_shielded = True
                    break
            if not point_is_shielded:
                all_points_shielded = False
                break

        if all_points_shielded:
            total_effective_time += DT

    return -total_effective_time  # GA minimizes, so we return negative for maximization


# ================== GA Optimization using scikit-opt ==================

# Parameter bounds: [angle, speed, release, delay] for each of the 3 UAVs
# lb: lower bounds, ub: upper bounds
lb = [0, 70, 0, 0.5] * 3
ub = [2 * np.pi, 140, 67, 20] * 3

# Estimate missile flight time to tighten bounds (optional but good practice)
dist_to_target = np.linalg.norm(R_M1_0 - T_BASE)
est_flight_time = dist_to_target / V_M1
print(f"Estimated missile flight time: {est_flight_time:.2f} seconds")

# Update release time upper bound based on flight time
for i in range(3):
    ub[i * 4 + 2] = min(ub[i * 4 + 2], est_flight_time)

print("Starting GA optimization...")

# Use a simple tqdm progress bar
pbar = tqdm(total=100, desc="GA Progress")


def on_generation(ga_instance):
    pbar.update(1)
    t = ga_instance.best_y
    if t == None:
        return
    pbar.set_postfix({"best_fitness": f"{-(ga_instance.best_y[-1]):.2f}s"})


class ProgressedGA(GA):
    def mutation(self):
        on_generation(self)
        return super().mutation()


ga = ProgressedGA(
    func=calculate_shielding_time,
    n_dim=12,
    size_pop=200,
    max_iter=100,  # Increased from 10 in matlab for better convergence
    prob_mut=0.01,
    lb=lb,
    ub=ub,
    precision=1e-7,
)

best_params, best_fitness = ga.run()
pbar.close()

# ================== Print Optimal Results ==================

print("\nOptimal Parameters Found:")
total_effective_time = -best_fitness

for i in range(3):
    angle, speed, t_release, t_delay = (
        best_params[i * 4],
        best_params[i * 4 + 1],
        best_params[i * 4 + 2],
        best_params[i * 4 + 3],
    )
    t_explosion = t_release + t_delay
    angle_deg = np.rad2deg(angle)

    e_fy = np.array([np.cos(angle), np.sin(angle), 0.0])
    release_pos = UAV_POSITIONS[i] + speed * t_release * e_fy
    explosion_pos = (
        release_pos
        + t_delay * speed * e_fy
        - 0.5 * G * t_delay**2 * np.array([0.0, 0.0, 1.0])
    )

    print(f"\n--- UAV {i+1} ---")
    print(
        f"  Strategy: Angle={angle_deg:.2f}°, Speed={speed:.2f} m/s, Release Time={t_release:.2f}s, Delay Time={t_delay:.2f}s"
    )
    print(f"  Timing: Explosion at {t_explosion:.2f}s")
    print(f"  Positions:")
    print(
        f"    Release: ({release_pos[0]:.2f}, {release_pos[1]:.2f}, {release_pos[2]:.2f})"
    )
    print(
        f"    Explosion: ({explosion_pos[0]:.2f}, {explosion_pos[1]:.2f}, {explosion_pos[2]:.2f})"
    )

print(f"\n==================================================")
print(f"Maximum Total Effective Shielding Time: {total_effective_time} seconds")
print(f"==================================================")
