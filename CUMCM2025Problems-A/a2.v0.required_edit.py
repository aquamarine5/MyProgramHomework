import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
v_min = 70.0
v_max = 140.0


def missile_position(t):
    return missile_pos0 + missile_speed * t * missile_dir


def cloud_center(t, detonate_pos, t_detonate):
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


def cover_time(theta, v, t_rel, delta_t, dt=0.01):
    release_pos = uav_pos0 + v * t_rel * np.array([np.cos(theta), np.sin(theta), 0.0])
    detonate_pos = release_pos + v * delta_t * np.array(
        [np.cos(theta), np.sin(theta), 0.0]
    )
    detonate_pos[2] = release_pos[2] - 0.5 * g * (delta_t**2)
    t_detonate = t_rel + delta_t
    t_vals = np.arange(t_detonate, t_detonate + cloud_valid_time, dt)
    covered = []
    for t in t_vals:
        covered.append(
            line_point_distance(
                missile_position(t),
                true_target,
                cloud_center(t, detonate_pos, t_detonate),
            )
            <= cloud_radius
        )
    covered = np.array(covered).astype(int)

    changes = np.diff(covered)
    entries = t_vals[1:][changes == 1]
    exits = t_vals[1:][changes == -1]

    if len(entries) > len(exits):
        exits = np.append(exits, t_vals[-1])
    if len(exits) > len(entries):
        entries = np.insert(entries, 0, t_vals[0])

    cover_intervals = list(zip(entries, exits))
    total_cover = sum([end - start for start, end in cover_intervals])
    return total_cover, cover_intervals, t_detonate, detonate_pos


def search():
    SCALE = 2
    theta_vals = np.linspace(np.deg2rad(175), np.deg2rad(178), SCALE * 6)
    v_vals = np.linspace(v_min, v_max, SCALE * 4)
    t_rel_vals = np.linspace(0.0, 1.0, SCALE * 2)
    delta_t_vals = np.linspace(2.0, 3.5, SCALE * 8)
    best = {"cover": 0}
    results = []
    for theta in theta_vals:
        for v in v_vals:
            for t_rel in t_rel_vals:
                for delta_t in delta_t_vals:
                    total_cover, intervals, t_detonate, detonate_pos = cover_time(
                        theta, v, t_rel, delta_t
                    )
                    results.append(
                        {
                            "cover": total_cover,
                            "theta": theta,
                            "v": v,
                            "t_rel": t_rel,
                            "delta_t": delta_t,
                        }
                    )
                    if total_cover > best["cover"]:
                        best.update(
                            {
                                "cover": total_cover,
                                "theta": theta,
                                "v": v,
                                "t_rel": t_rel,
                                "delta_t": delta_t,
                                "intervals": intervals,
                                "t_detonate": t_detonate,
                                "detonate_pos": detonate_pos,
                            }
                        )
    print(f"theta: {np.rad2deg(best['theta']):.2f} v={best['v']:.2f}")
    print(f"t_rel: {best['t_rel']:.2f} deltaT={best['delta_t']:.2f}s")
    print(f"t_det={best['t_detonate']:.2f}s, point={best['detonate_pos']}")
    print(f"TIME={best['cover']:.2f}s")

    df = pd.DataFrame(results)
    best_theta = best["theta"]
    best_v = best["v"]
    best_t_rel = best["t_rel"]
    best_delta_t = best["delta_t"]
    max_cover = best["cover"]

    plt.figure(figsize=(12, 10))

    # Plot cover vs delta_t
    plt.subplot(2, 2, 1)
    subset = df[
        (df["theta"] == best_theta) & (df["v"] == best_v) & (df["t_rel"] == best_t_rel)
    ]
    plt.plot(subset["delta_t"], subset["cover"])
    plt.scatter(
        best_delta_t,
        max_cover,
        color="red",
        marker="*",
        s=150,
        zorder=5,
        label="Max Cover",
    )
    plt.xlabel("delta_t (s)")
    plt.ylabel("Cover Time (s)")
    plt.title("Cover Time vs. delta_t")
    plt.legend()
    plt.grid(True)

    # Plot cover vs t_rel
    plt.subplot(2, 2, 2)
    subset = df[
        (df["theta"] == best_theta)
        & (df["v"] == best_v)
        & (df["delta_t"] == best_delta_t)
    ]
    plt.plot(subset["t_rel"], subset["cover"])
    plt.scatter(best_t_rel, max_cover, color="red", marker="*", s=150, zorder=5)
    plt.xlabel("t_rel (s)")
    plt.ylabel("Cover Time (s)")
    plt.title("Cover Time vs. t_rel")
    plt.grid(True)

    # Plot cover vs v
    plt.subplot(2, 2, 3)
    subset = df[
        (df["theta"] == best_theta)
        & (df["t_rel"] == best_t_rel)
        & (df["delta_t"] == best_delta_t)
    ]
    plt.plot(subset["v"], subset["cover"])
    plt.scatter(best_v, max_cover, color="red", marker="*", s=150, zorder=5)
    plt.xlabel("v (m/s)")
    plt.ylabel("Cover Time (s)")
    plt.title("Cover Time vs. UAV Speed (v)")
    plt.grid(True)

    # Plot cover vs theta
    plt.subplot(2, 2, 4)
    subset = df[
        (df["v"] == best_v)
        & (df["t_rel"] == best_t_rel)
        & (df["delta_t"] == best_delta_t)
    ]
    plt.plot(np.rad2deg(subset["theta"]), subset["cover"])
    plt.scatter(
        np.rad2deg(best_theta), max_cover, color="red", marker="*", s=150, zorder=5
    )
    plt.xlabel("theta (degrees)")
    plt.ylabel("Cover Time (s)")
    plt.title("Cover Time vs. UAV Angle (theta)")
    plt.grid(True)

    plt.tight_layout()

    # Create heatmap for theta and delta_t
    plt.figure(figsize=(8, 6))
    heatmap_data = df[(df["v"] == best_v) & (df["t_rel"] == best_t_rel)]
    pivot_table = heatmap_data.pivot_table(
        index="delta_t", columns="theta", values="cover"
    )

    # Convert theta from radians to degrees for the labels
    pivot_table.columns = np.rad2deg(pivot_table.columns)

    X, Y = np.meshgrid(pivot_table.columns, pivot_table.index)

    plt.pcolormesh(X, Y, pivot_table.values, shading="auto", cmap="viridis")
    plt.colorbar(label="Cover Time (s)")
    plt.scatter(
        np.rad2deg(best_theta),
        best_delta_t,
        color="red",
        marker="*",
        s=200,
        label="Max Cover",
    )
    plt.xlabel("theta (degrees)")
    plt.ylabel("delta_t (s)")
    plt.title(f"Cover Time Heatmap (v={best_v:.2f}, t_rel={best_t_rel:.2f})")
    plt.legend()
    plt.grid(True)

    plt.show()


search()
