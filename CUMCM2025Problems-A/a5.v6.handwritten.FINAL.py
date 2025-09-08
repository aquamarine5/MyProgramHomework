import datetime
import sys
from time import time
import numba
from numpy.typing import NDArray
import numpy as npy
from typing import List, Optional, Tuple, Dict
from tqdm import tqdm
import pandas as pd

Vector3 = NDArray[npy.float64]

minCloudInterval = 1.0
maxCloudPerFY = 3
posMissilesList: NDArray[npy.float64] = npy.array(
    [
        [20000.0, 0.0, 2000.0],  # M1
        [19000.0, 600.0, 2100.0],  # M2
        [18000.0, -600.0, 1900.0],  # M3
    ]
)
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])
directionsMissile: NDArray[npy.float64] = npy.array(
    [
        (posMissileTarget - pos) / npy.linalg.norm(posMissileTarget - pos)
        for pos in posMissilesList
    ]
)
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
posFakeTarget = posMissileTarget
rRealTarget = 7
hRealTarget = 10
posFYsList: NDArray[npy.float64] = npy.array(
    [
        [17800.0, 0.0, 1800.0],  # FY1
        [12000.0, 1400.0, 1400.0],  # FY2
        [6000.0, -3000.0, 700.0],  # FY3
        [11000.0, 2000.0, 1800.0],  # FY4
        [13000.0, -2000.0, 1300.0],  # FY5
    ]
)
speedFYMin = 70.0
speedFYMax = 140.0
G = 9.8
DT = 0.02
RANGE_STEP = 30
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

tCalculateRange = npy.arange(0.0, 60.0, DT, dtype=npy.float32)


@numba.njit()
def getMissilePosition(t: float, missileId: int) -> Vector3:
    return posMissilesList[missileId] + speedMissile * t * directionsMissile[missileId]


@numba.njit()
def getCloudPosition(t: float, posDetonate: Vector3, tDetonate: float) -> Vector3:
    return npy.array(
        [posDetonate[0], posDetonate[1], posDetonate[2] - speedCloud * (t - tDetonate)]
    )


@numba.jit()
def distancePoint2Line(
    linePoint1: Vector3, linePoint2: Vector3, targetPoint: Vector3
) -> float:
    lineVec: Vector3 = linePoint2 - linePoint1
    pointVec: Vector3 = targetPoint - linePoint1
    s = npy.dot(lineVec, pointVec) / npy.dot(lineVec, lineVec)
    s_clamped = max(0.0, min(s, 1.0))
    closest = linePoint1 + s_clamped * lineVec
    return npy.linalg.norm(targetPoint - closest)


@numba.njit()
def calculateIntersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)
    pointsIntersection = []
    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]
        if x < 0:
            pointsIntersection.append(npy.array([x, y, posRealTarget[2] + hRealTarget]))
        if x > 0:
            pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))
    return pointsIntersection


@numba.njit()
def calculatePerpendicularIntersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)
    directionPerpendicular = npy.array([-directionMissile[1], directionMissile[0]])
    pointsIntersection = []
    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionPerpendicular[0]
        y = posRealTarget[1] + sign * rRealTarget * directionPerpendicular[1]

        pointsIntersection.append(npy.array([x, y, posRealTarget[2] + hRealTarget]))
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))
    return pointsIntersection


@numba.njit()
def calculateCheckpoints(t: float, missileId: int) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t, missileId)
    points = numba.typed.List()
    points_cylinder = calculateIntersection(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    points_perp = calculatePerpendicularIntersection(posNowMissile)
    for p in points_perp:
        points.append(p)
    return points


@numba.jit()
def checkLineIntersectSphere(
    linePoint1: Vector3, linePoint2: Vector3, sphereCenter: Vector3, sphereRadius: float
) -> bool:
    return distancePoint2Line(linePoint1, linePoint2, sphereCenter) <= sphereRadius


@numba.njit()
def calculateSingleCloudMask(
    posFY: Vector3, angleDeg: float, speedFY: float, tRelease: float, tDelay: float
) -> NDArray[npy.bool_]:
    angleRad = angleDeg * npy.pi / 180.0
    directionFY: Vector3 = npy.array([npy.cos(angleRad), npy.sin(angleRad), 0.0])
    posRelease: Vector3 = posFY + directionFY * speedFY * tRelease
    vRelease: Vector3 = directionFY * speedFY
    posDetonate: Vector3 = (
        posRelease
        + vRelease * tDelay
        + npy.array([0.0, 0.0, -0.5 * G * tDelay * tDelay])
    )
    tDetonate = tRelease + tDelay
    isMaskedList = npy.zeros(
        (len(posMissilesList), len(tCalculateRange)), dtype=npy.bool_
    )
    tMaskedStart = tDetonate
    tMaskedEnd = tDetonate + tCloud
    for index, instant in enumerate(tCalculateRange):
        if not (tMaskedStart <= instant <= tMaskedEnd):
            continue
        posCloudInstant = getCloudPosition(instant, posDetonate, tDetonate)
        for missileId in range(len(posMissilesList)):
            posMissileInstant = getMissilePosition(instant, missileId)
            isCovered = True
            for checkpoint in calculateCheckpoints(instant, missileId):
                if not checkLineIntersectSphere(
                    posMissileInstant, checkpoint, posCloudInstant, rCloud
                ):
                    isCovered = False
                    break
            isMaskedList[missileId, index] = isCovered
    return isMaskedList


def generateFYCandidates(idFY: int, posFY: Vector3) -> list[dict]:
    angles = npy.linspace(0, 360, RANGE_STEP)
    speeds = npy.linspace(speedFYMin, speedFYMax, RANGE_STEP)
    tReleases = npy.linspace(1.0, 60.0, RANGE_STEP)
    tDelays = npy.linspace(0.5, 20.0, RANGE_STEP)
    progressbar = tqdm(
        total=len(angles) * len(speeds) * len(tReleases) * len(tDelays),
        desc=f"FY{idFY+1}",
        leave=False,
    )
    candidatesList = []
    for angle in angles:
        for speed in speeds:
            for tRelease in tReleases:
                for tDelay in tDelays:
                    isMasked = calculateSingleCloudMask(
                        posFY, angle, speed, tRelease, tDelay
                    )
                    if npy.any(isMasked):
                        candidatesList.append(
                            {
                                "angle": angle,
                                "speed": speed,
                                "tRelease": tRelease,
                                "tDelay": tDelay,
                                "isMasked": isMasked,
                                "idFY": idFY,
                            }
                        )
                    progressbar.update(1)
    progressbar.close()
    return candidatesList


def calculateGreedySolution() -> Tuple[List[Dict], NDArray[npy.float64]]:
    allCandidatesList: Dict[int, List[Dict]] = {}
    allCandidatesFlat = []
    for idFY, posFY in enumerate(posFYsList):
        candidates = generateFYCandidates(idFY, posFY)
        allCandidatesList[idFY] = candidates
        allCandidatesFlat.extend(candidates)
        print(f"FY{idFY+1} candidates: {len(candidates)}")
    print(f"Total candidates: {len(allCandidatesFlat)}")
    allCandidatesFlat.sort(key=lambda x: npy.sum(x["isMasked"]), reverse=True)
    finalPlan = []
    totalCloud = maxCloudPerFY * len(posFYsList)
    unionMaskedList = npy.zeros(
        (len(posMissilesList), len(tCalculateRange)), dtype=npy.bool_
    )
    greedyFYLockedList = {
        id_: {
            "locked": False,
            "angle": None,
            "speed": None,
            "tRelease": [],
            "maskedCount": 0,
        }
        for id_ in range(len(posFYsList))
    }
    progressbarState = tqdm(total=totalCloud, desc="Greedy Selection")

    for indexCloud in range(totalCloud):
        bestCandidate = None
        tMaxGain = -1.0
        for candidate in allCandidatesFlat:
            idFY = candidate["idFY"]
            FYState = greedyFYLockedList[idFY]
            if FYState["maskedCount"] >= maxCloudPerFY:
                continue

            if FYState["locked"]:
                if not (
                    npy.isclose(candidate["angle"], FYState["angle"])
                    and npy.isclose(candidate["speed"], FYState["speed"])
                ):
                    continue

            isTooClosed = False
            for tRelease in FYState["tRelease"]:
                if abs(tRelease - candidate["tRelease"]) < minCloudInterval:
                    isTooClosed = True
                    break
            if isTooClosed:
                continue

            tCurrentTotalMasked = npy.sum(unionMaskedList) * DT
            newUnionMaskedList = unionMaskedList | candidate["isMasked"]
            tNewTotalMasked = npy.sum(newUnionMaskedList) * DT
            tGain = tNewTotalMasked - tCurrentTotalMasked
            if tGain > tMaxGain:
                tMaxGain = tGain
                bestCandidate = candidate
        if bestCandidate is None or tMaxGain <= DT:
            print(
                f"In {indexCloud} No more valid candidates or no gain, stopping selection."
            )
            break
        finalPlan.append(bestCandidate)
        unionMaskedList |= bestCandidate["isMasked"]
        FYState = greedyFYLockedList[bestCandidate["idFY"]]
        FYState["tRelease"].append(bestCandidate["tRelease"])
        FYState["maskedCount"] += 1
        if not FYState["locked"]:
            FYState["locked"] = True
            FYState["angle"] = bestCandidate["angle"]
            FYState["speed"] = bestCandidate["speed"]
        progressbarState.update(1)
        progressbarState.set_postfix({"t": f"{tMaxGain:.2f}"})
    progressbarState.close()
    return finalPlan, unionMaskedList


def saveResults(finalPlan: List[Dict], unionMaskedList: NDArray):
    print("\n3. 正在处理并保存结果...")
    if not finalPlan:
        print("未找到可行的投放计划。")
        return

    results_data = []
    for plan in finalPlan:
        idFY = plan["idFY"]
        uav_id = f"FY{idFY + 1}"
        pos_uav_0 = posFYsList[idFY]
        angle_deg = plan["angle"]
        speed = plan["speed"]
        tRelease = plan["tRelease"]
        tDelay = plan["tDelay"]

        angle_rad = npy.deg2rad(angle_deg)
        directionFYs = npy.array([npy.cos(angle_rad), npy.sin(angle_rad), 0.0])
        posRelease: Vector3 = pos_uav_0 + speed * tRelease * directionFYs
        vRelease: Vector3 = speed * directionFYs
        posDetonate: Vector3 = (
            posRelease
            + vRelease * tDelay
            - 0.5 * G * tDelay**2 * npy.array([0.0, 0.0, 1.0])
        )

        tSingleMasked = npy.sum(plan["isMasked"]) * DT

        results_data.append(
            {
                "无人机编号": uav_id,
                "无人机运动方向 (deg)": angle_deg,
                "无人机运动速度 (m/s)": speed,
                "烟幕弹投放时刻 (s)": tRelease,
                "烟幕弹引信延迟 (s)": tDelay,
                "投放点x": posRelease[0],
                "投放点y": posRelease[1],
                "投放点z": posRelease[2],
                "起爆点x": posDetonate[0],
                "起爆点y": posDetonate[1],
                "起爆点z": posDetonate[2],
                "单弹贡献总时长 (s)": tSingleMasked,
            }
        )

    df = pd.DataFrame(results_data)

    df: pd.DataFrame = df.sort_values(
        by=["无人机编号", "烟幕弹投放时刻 (s)"]
    ).reset_index(drop=True)
    df.insert(0, "烟幕弹总编号", df.index + 1)

    timestamp = datetime.datetime.now().strftime("%H%M%S")
    output_path = f"A题/result5_greedy_{timestamp}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"  - 详细投放计划已保存到: {output_path}")
    tTotalMasked = npy.sum(unionMaskedList) * DT
    tMaskedMissile1 = npy.sum(unionMaskedList[0, :]) * DT
    tMaskedMissile2 = npy.sum(unionMaskedList[1, :]) * DT
    tMaskedMissile3 = npy.sum(unionMaskedList[2, :]) * DT

    print("\n--- 最终结果 ---")
    print(f"总计投放 {len(finalPlan)} 枚烟幕弹。")
    print(f"导弹M1有效遮蔽时间: {tMaskedMissile1:.2f} s")
    print(f"导弹M2有效遮蔽时间: {tMaskedMissile2:.2f} s")
    print(f"导弹M3有效遮蔽时间: {tMaskedMissile3:.2f} s")
    print(f"所有导弹遮蔽时间总和: {tTotalMasked:.2f} s")


def draw_3d_visualization(final_plan: List[Dict], union_masked_list: NDArray):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from collections import defaultdict

    fig = plt.figure(figsize=(18, 14))
    axis = fig.add_subplot(111, projection="3d")
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    plan_by_fy = defaultdict(list)
    for plan in final_plan:
        plan_by_fy[plan["idFY"]].append(plan)

    DRAW_DT = 0.1
    missile_colors = [("red", "black"), ("blue", "black"), ("green", "black")]
    t_max_missile = 80.0
    t_iterator_missile = npy.arange(0, t_max_missile, DRAW_DT)

    for missile_id in range(len(posMissilesList)):
        traj_missile = npy.array(
            [getMissilePosition(t, missile_id) for t in t_iterator_missile]
        )
        time_indices = (t_iterator_missile / DT).astype(int)
        valid_indices = time_indices < union_masked_list.shape[1]
        is_covered = npy.zeros_like(t_iterator_missile, dtype=bool)
        is_covered[valid_indices] = union_masked_list[
            missile_id, time_indices[valid_indices]
        ]

        uncovered_color, covered_color = missile_colors[missile_id]
        colors_traj = npy.where(is_covered, covered_color, uncovered_color)

        points = traj_missile.reshape(-1, 1, 3)
        segments = npy.concatenate([points[:-1], points[1:]], axis=1)
        axis.add_collection(
            Line3DCollection(segments, colors=colors_traj[:-1], linewidths=2, alpha=0.7)
        )
        axis.scatter(
            *posMissilesList[missile_id],
            color=uncovered_color,
            s=50,
            label=f"导弹M{missile_id+1}发射点",
        )

    fy_colors = ["cyan", "magenta", "yellow", "purple", "orange"]
    for idFY, plans in plan_by_fy.items():
        if not plans:
            continue
        first_plan = plans[0]
        angle_deg = first_plan["angle"]
        speed = first_plan["speed"]
        angle_rad = npy.deg2rad(angle_deg)
        directionFY = npy.array([npy.cos(angle_rad), npy.sin(angle_rad), 0.0])
        pos_fy_initial = posFYsList[idFY]
        fy_color = fy_colors[idFY % len(fy_colors)]
        max_t_release = max(p["tRelease"] for p in plans)
        traj_fy = npy.array(
            [
                pos_fy_initial + speed * t * directionFY
                for t in npy.arange(0, max_t_release + 1, DRAW_DT)
            ]
        )
        axis.plot(
            traj_fy[:, 0],
            traj_fy[:, 1],
            traj_fy[:, 2],
            color=fy_color,
            linestyle="--",
            label=f"无人机FY{idFY+1}轨迹",
        )
        for i, plan in enumerate(plans):
            tRelease = plan["tRelease"]
            tDelay = plan["tDelay"]
            tDetonate = tRelease + tDelay

            posRelease = pos_fy_initial + speed * tRelease * directionFY
            vRelease = speed * directionFY
            posDetonate = (
                posRelease
                + vRelease * tDelay
                - 0.5 * G * tDelay**2 * npy.array([0.0, 0.0, 1.0])
            )
            t_decoy_iterator = npy.arange(tRelease, tDetonate, DRAW_DT)
            traj_decoy = npy.array(
                [
                    posRelease
                    + vRelease * (t - tRelease)
                    - 0.5 * G * (t - tRelease) ** 2 * npy.array([0.0, 0.0, 1.0])
                    for t in t_decoy_iterator
                ]
            )
            if traj_decoy.size > 0:
                axis.plot(
                    traj_decoy[:, 0],
                    traj_decoy[:, 1],
                    traj_decoy[:, 2],
                    color="darkgreen",
                    linestyle="dotted",
                    label=f"干扰弹轨迹" if idFY == 0 and i == 0 else "",
                )

            traj_smoke_sink = npy.array(
                [
                    getCloudPosition(t, posDetonate, tDetonate)
                    for t in npy.arange(tDetonate, tDetonate + tCloud, DRAW_DT)
                ]
            )
            if traj_smoke_sink.size > 0:
                axis.plot(
                    traj_smoke_sink[:, 0],
                    traj_smoke_sink[:, 1],
                    traj_smoke_sink[:, 2],
                    color="gray",
                    linestyle="-",
                    label=f"烟雾下沉轨迹" if idFY == 0 and i == 0 else "",
                )

            u, v = npy.linspace(0, 2 * npy.pi, 20), npy.linspace(0, npy.pi, 20)
            for center in traj_smoke_sink[::20]:
                x = center[0] + rCloud * npy.outer(npy.cos(u), npy.sin(v))
                y = center[1] + rCloud * npy.outer(npy.sin(u), npy.sin(v))
                z = center[2] + rCloud * npy.outer(npy.ones(npy.size(u)), npy.cos(v))
                axis.plot_surface(x, y, z, color="gray", alpha=0.05, linewidth=0)
            axis.scatter(
                *posRelease,
                color="brown",
                s=30,
                label=f"投放点" if idFY == 0 and i == 0 else "",
            )
            axis.scatter(
                *posDetonate,
                color="purple",
                s=30,
                label=f"爆炸点" if idFY == 0 and i == 0 else "",
            )

    axis.scatter(*posRealTarget, color="black", s=100, marker="*", label="真实目标")
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="gray", alpha=0.3, label="烟幕云覆盖区域"),
        plt.Line2D([0], [0], color="red", lw=2, label="M1轨迹(未遮蔽)"),
        plt.Line2D([0], [0], color="blue", lw=2, label="M2轨迹(未遮蔽)"),
        plt.Line2D([0], [0], color="green", lw=2, label="M3轨迹(未遮蔽)"),
        plt.Line2D([0], [0], color="black", lw=2, label="导弹轨迹(被遮蔽)"),
        plt.Line2D(
            [0], [0], color="cyan", lw=2, linestyle="--", label="无人机轨迹(示例)"
        ),
        plt.Line2D(
            [0], [0], color="darkgreen", lw=2, linestyle="dotted", label="干扰弹轨迹"
        ),
        plt.Line2D([0], [0], color="gray", lw=2, label="烟雾下沉轨迹"),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="投放点",
            markerfacecolor="brown",
            markersize=8,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="爆炸点",
            markerfacecolor="purple",
            markersize=8,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            label="真实目标",
            markerfacecolor="black",
            markersize=12,
        ),
    ]
    axis.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1.05, 0.5))

    axis.set_xlabel("X (m)")
    axis.set_ylabel("Y (m)")
    axis.set_zlabel("Z (m)")
    axis.set_title("多无人机多烟幕弹协同遮蔽三维轨迹示意图")

    all_points = []
    for plans in plan_by_fy.values():
        for plan in plans:
            idFY = plan["idFY"]
            angle_deg = plan["angle"]
            speed = plan["speed"]
            tRelease = plan["tRelease"]
            tDelay = plan["tDelay"]
            angle_rad = npy.deg2rad(angle_deg)
            directionFY = npy.array([npy.cos(angle_rad), npy.sin(angle_rad), 0.0])
            pos_fy_initial = posFYsList[idFY]
            posRelease = pos_fy_initial + speed * tRelease * directionFY
            vRelease = speed * directionFY
            posDetonate = (
                posRelease
                + vRelease * tDelay
                - 0.5 * G * tDelay**2 * npy.array([0.0, 0.0, 1.0])
            )
            all_points.append(posRelease)
            all_points.append(posDetonate)

    if all_points:
        all_points = npy.array(all_points)
        x_min, x_max = npy.min(all_points[:, 0]), npy.max(all_points[:, 0])
        y_min, y_max = npy.min(all_points[:, 1]), npy.max(all_points[:, 1])
        z_min, z_max = npy.min(all_points[:, 2]), npy.max(all_points[:, 2])
        center = npy.array(
            [
                npy.mean([x_min, x_max]),
                npy.mean([y_min, y_max]),
                npy.mean([z_min, z_max]),
            ]
        )
        max_range = npy.max([x_max - x_min, y_max - y_min, z_max - z_min]) * 1.2
        axis.set_xlim(center[0] - max_range / 2, center[0] + max_range / 2)
        axis.set_ylim(center[1] - max_range / 2, center[1] + max_range / 2)
        axis.set_zlim(center[2] - max_range / 2, center[2] + max_range / 2)

    plt.tight_layout()
    plt.show()


finalPlan, unionMaskedList = calculateGreedySolution()
saveResults(finalPlan, unionMaskedList)
draw_3d_visualization(finalPlan, unionMaskedList)
