import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

missile_pos0 = np.array([20000.0, 0.0, 2000.0])
missile_speed = 300.0
missile_target = np.array([0.0, 0.0, 0.0])
missile_dir = (missile_target - missile_pos0) / np.linalg.norm(
    missile_target - missile_pos0
)

true_target = np.array([0.0, 200.0, 0.0])

uav_pos0 = np.array([17800.0, 0.0, 1800.0])
uav_speed = 120.0
uav_dir = np.array([-1.0, 0.0, 0.0])
t_release = 1.5
t_delay = 3.6
t_detonate = t_release + t_delay
g = 9.8
release_pos = uav_pos0 + uav_speed * t_release * uav_dir
detonate_pos = release_pos + uav_speed * t_delay * uav_dir
detonate_pos[2] = release_pos[2] - 0.5 * g * (t_delay**2)

cloud_radius = 10.0
cloud_sink_speed = 3.0
cloud_valid_time = 20.0


def missile_position(t):
    return missile_pos0 + missile_speed * t * missile_dir


def cloud_center(t):
    return np.array(
        [
            detonate_pos[0],
            detonate_pos[1],
            detonate_pos[2] - cloud_sink_speed * (t - t_detonate),
        ]
    )


def line_point_distance(p1, p2, c):
    v = p2 - p1
    w = c - p1
    s = np.dot(v, w) / np.dot(v, v)
    s_clamped = np.clip(s, 0.0, 1.0)
    closest = p1 + s_clamped * v
    return np.linalg.norm(c - closest)


def is_covered(t):
    if t < t_detonate or t > t_detonate + cloud_valid_time:
        return False
    mpos = missile_position(t)
    cpos = cloud_center(t)
    d = line_point_distance(mpos, true_target, cpos)
    return d <= cloud_radius


dt = 0.01
t_vals = np.arange(0, t_detonate + cloud_valid_time + 1, dt)
covered = np.array([is_covered(t) for t in t_vals])

mask = covered.astype(int)
changes = np.diff(mask)
entries = t_vals[1:][changes == 1]
exits = t_vals[1:][changes == -1]

if len(entries) > len(exits):
    exits = np.append(exits, t_vals[-1])
if len(exits) > len(entries):
    entries = np.insert(entries, 0, t_vals[0])

cover_intervals = list(zip(entries, exits))
total_cover = sum([end - start for start, end in cover_intervals])
print(f"total covered time: {total_cover:.8f} seconds")
plt.figure(figsize=(10, 6))
plt.plot(t_vals, covered, label="Covered Status", lw=2)
for start, end in cover_intervals:
    plt.axvspan(start, end, color="orange", alpha=0.3)
plt.axvline(t_detonate, color="red", ls="--", label="Detonation Time")
plt.axvline(
    t_detonate + cloud_valid_time, color="green", ls="--", label="Cloud Expiry Time"
)
plt.xlabel("Time (s)")
plt.ylabel("Covered (1=True, 0=False)")
plt.grid()
plt.show()


# 3D Visualization
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# Time array for plotting trajectories
t_max = 20000.0 / missile_speed  # Time for missile to reach origin
t_plot = np.arange(0, t_max, 0.01)

# --- Trajectories ---
# Missile trajectory
missile_traj = np.array([missile_position(t) for t in t_plot])

# UAV trajectory
uav_traj = uav_pos0 + uav_speed * t_plot[:, np.newaxis] * uav_dir

# Decoy (smoke grenade) trajectory
t_decoy_fall = np.arange(t_release, t_detonate, 0.1)
decoy_traj_x = release_pos[0] + uav_speed * (t_decoy_fall - t_release) * uav_dir[0]
decoy_traj_y = np.full_like(t_decoy_fall, release_pos[1])
decoy_traj_z = release_pos[2] - 0.5 * g * ((t_decoy_fall - t_release) ** 2)

# Smoke cloud center trajectory
t_smoke_sink = np.arange(t_detonate, t_detonate + cloud_valid_time, 0.1)
smoke_center_traj = np.array([cloud_center(t) for t in t_smoke_sink])


# --- Plotting ---
# Trajectories
ax.plot(
    uav_traj[:, 0],
    uav_traj[:, 1],
    uav_traj[:, 2],
    label="无人机轨迹",
    color="blue",
    linestyle="--",
)

# Plot missile trajectory with changing color
missile_covered_status = np.array([is_covered(t) for t in t_plot])
colors = np.where(missile_covered_status, "yellow", "red")

# Create segments from the trajectory points
points = missile_traj.reshape(-1, 1, 3)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Create a Line3DCollection and add it to the axes
lc = Line3DCollection(segments, colors=colors[:-1], linewidths=2)
ax.add_collection(lc)


ax.plot(
    decoy_traj_x,
    decoy_traj_y,
    decoy_traj_z,
    label="干扰弹轨迹",
    color="green",
    linestyle=":",
)
ax.plot(
    smoke_center_traj[:, 0],
    smoke_center_traj[:, 1],
    smoke_center_traj[:, 2],
    label="烟雾中心轨迹",
    color="gray",
    linestyle="-.",
)

# Points
ax.scatter(*missile_pos0, color="red", s=50, label="导弹初始位置")
ax.scatter(*true_target, color="darkgreen", s=100, marker="*", label="真目标")
ax.scatter(*release_pos, color="purple", s=80, marker="D", label="干扰弹投掷位置")
ax.scatter(*detonate_pos, color="orange", s=80, label="干扰弹引爆位置")

# Plot multiple smoke spheres to show the volume over time
u = np.linspace(0, 2 * np.pi, 30)  # Lower resolution for performance
v = np.linspace(0, np.pi, 30)
# Plot a sphere at different points in the smoke's trajectory
for center in smoke_center_traj[::20]:  # Plot every 20th point to avoid clutter
    x = center[0] + cloud_radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + cloud_radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + cloud_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color="gray", alpha=0.1, linewidth=0)


# --- Formatting ---
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_zlabel("Z (m)")
ax.set_title("战场态势3D可视化")

# Set plot limits and aspect ratio
x_lims = (17100, 17650)
y_lims = (0, 50)
z_lims = (1600, 2000)
ax.set_xlim(x_lims)
ax.set_ylim(y_lims)
ax.set_zlim(z_lims)
ax.set_box_aspect(
    (np.ptp(x_lims), np.ptp(y_lims), np.ptp(z_lims))
)  # To make spheres look like spheres

# Create a custom legend for the surface plot
from matplotlib.patches import Patch

legend_elements = [
    plt.Line2D([0], [0], color="blue", linestyle="--", label="无人机轨迹"),
    plt.Line2D([0], [0], color="red", label="导弹轨迹 (未覆盖)"),
    plt.Line2D([0], [0], color="yellow", label="导弹轨迹 (被覆盖)"),
    plt.Line2D([0], [0], color="green", linestyle=":", label="干扰弹轨迹"),
    plt.Line2D([0], [0], color="gray", linestyle="-.", label="烟雾中心轨迹"),
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="red",
        markersize=7,
        label="导弹初始位置",
    ),
    plt.Line2D(
        [0],
        [0],
        marker="*",
        color="w",
        markerfacecolor="darkgreen",
        markersize=10,
        label="真目标",
    ),
    plt.Line2D(
        [0],
        [0],
        marker="D",
        color="w",
        markerfacecolor="purple",
        markersize=7,
        label="干扰弹投掷位置",
    ),
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="orange",
        markersize=7,
        label="干扰弹引爆位置",
    ),
    Patch(facecolor="gray", alpha=0.3, label="烟雾覆盖范围"),
]
ax.legend(handles=legend_elements, loc="best")


plt.show()
