import numba
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from tqdm import tqdm

Vector3 = NDArray[npy.float64]
Trajectory = List[Vector3]  # or NDArray[npy.float64]

posMissile: Vector3 = npy.array([20000.0, 0.0, 2000.0])
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])
directionMissile: Vector3 = (posMissileTarget - posMissile) / npy.linalg.norm(
    posMissileTarget - posMissile
)
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
rRealTarget = 7
hRealTarget = 10
posFY1: Vector3 = npy.array([17800.0, 0.0, 1800.0])

from numba.typed import List as NumbaList
from numba.experimental import jitclass

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


@numba.jit()
def getMissilePosition(t: float) -> Vector3:
    return posMissile + speedMissile * t * directionMissile


@numba.jit()
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


@numba.jit()
def calculate_intersection_with_cylinder(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]
    # if npy.linalg.norm(v2directionMissile) == 0:
    #     return []

    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)

    pointsIntersection = []

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionMissile[0]
        y = posRealTarget[1] + sign * rRealTarget * directionMissile[1]

        pointsIntersection.append(
            npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        )
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部

    return pointsIntersection


@numba.jit()
def calculate_perpendicular_plane_intersection(posMissile: Vector3) -> List[Vector3]:
    v2directionMissile = posMissile[:2] - posRealTarget[:2]

    # if npy.linalg.norm(v2directionMissile) == 0:
    #     return []

    directionMissile = v2directionMissile / npy.linalg.norm(v2directionMissile)

    directionPerpendicular = npy.array([-directionMissile[1], directionMissile[0]])

    pointsIntersection = []

    for sign in [1, -1]:
        x = posRealTarget[0] + sign * rRealTarget * directionPerpendicular[0]
        y = posRealTarget[1] + sign * rRealTarget * directionPerpendicular[1]

        pointsIntersection.append(
            npy.array([x, y, posRealTarget[2] + hRealTarget])  # 顶部
        )
        pointsIntersection.append(npy.array([x, y, posRealTarget[2]]))  # 底部

    return pointsIntersection


@numba.jit()
def get6points(t: float) -> List[Vector3]:
    ax = (1400 * (20000 - 3000 * npy.sqrt(101) / 101 * t)) / (
        200 * npy.sqrt((20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2 + 40000)
    )
    ay = 200 + (1400) / (
        npy.sqrt(((20000 - 3000 * npy.sqrt(101) / 101 * t)) ** 2 + 40000)
    )
    az = 10
    bx = -ax
    by = 200 - (1400) / (
        npy.sqrt(((20000 - 3000 * npy.sqrt(101) / 101 * t)) ** 2 + 40000)
    )
    bz = 10
    cx = 1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    cy = 200 + 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / npy.sqrt(
        200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2
    )
    cz = 10
    dx = -1400 / npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    dy = 200 - 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / (
        npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    )
    dz = 10
    ex = (1400 * (20000 - 3000 * npy.sqrt(101) / 101 * t)) / (
        200 * npy.sqrt((20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2 + 200 * 200)
    )
    ey = 200 - (
        1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    )
    ez = 0
    fx = -ex
    fy = 200 + (
        1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    )
    fz = 0
    gx = 1400 / (npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2))
    gy = 200 + 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / (
        npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    )
    gz = 0
    hx = -gx
    hy = 200 - 7 * (20000 - 3000 * npy.sqrt(101) / 101 * t) / (
        npy.sqrt(200 * 200 + (20000 - 3000 * npy.sqrt(101) / 101 * t) ** 2)
    )
    hz = 0
    result = []
    if ax < 0:
        result.append(npy.array([ax, ay, az]))
    if bx < 0:
        result.append(npy.array([bx, by, bz]))
    if ex > 0:
        result.append(npy.array([ex, ey, ez]))
    if fx > 0:
        result.append(npy.array([fx, fy, fz]))
    return [
        npy.array([cx, cy, cz]),
        npy.array([dx, dy, dz]),
        npy.array([gx, gy, gz]),
        npy.array([hx, hy, hz]),
    ]


@numba.jit()
def calculateCheckpoints(t: float) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t)

    # Use a Numba typed list for compatibility
    points = []

    # Manually append items from the first function call
    points_cylinder = calculate_intersection_with_cylinder(posNowMissile)
    for p in points_cylinder:
        points.append(p)

    # Manually append items from the second function call
    points_perp = calculate_perpendicular_plane_intersection(posNowMissile)
    for p in points_perp:
        points.append(p)

    return points


@numba.jit()
def checkCovered(t: float, tDetonate: float, posDetonate: Vector3) -> bool:
    if t < tDetonate or t > tDetonate + tCloud:
        return False
    posNowMissile = getMissilePosition(t)
    checkpoints = calculateCheckpoints(t)

    for checkpoint in checkpoints:
        d = distancePoint2Line(
            posNowMissile, checkpoint, getCloudPosition(t, posDetonate, tDetonate)
        )
        if d > rCloud:
            return False
    return True


DT = 0.01


@numba.jit()
def calculateCoverTime(
    thetaFY1: float, vFY1: float, tRelease: float, tDelay: float
) -> CoverResult:
    posRelease: Vector3 = posFY1 + vFY1 * tRelease * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate: Vector3 = posRelease + vFY1 * tDelay * npy.array(
        [npy.cos(thetaFY1), npy.sin(thetaFY1), 0.0]
    )
    posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
    tDetonate = tRelease + tDelay
    iterator = npy.arange(0, tDetonate + tCloud + 1, DT)

    tTotalCovered = 0.0
    is_covered = False
    start_cover_time = 0.0

    for t in iterator:
        currently_covered = checkCovered(t, tDetonate, posDetonate)
        if currently_covered and not is_covered:
            is_covered = True
            start_cover_time = t
        elif not currently_covered and is_covered:
            is_covered = False
            tTotalCovered += t - start_cover_time

    if is_covered:
        tTotalCovered += iterator[-1] - start_cover_time

    return CoverResult(
        tTotalCovered, thetaFY1, vFY1, tRelease, tDelay, tDetonate, posDetonate
    )


def detonation_state(
    theta: float, v: float, tRelease: float, tDelay: float
) -> Tuple[float, Vector3]:
    u = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    posRelease: Vector3 = posFY1 + v * tRelease * u
    posDetonate: Vector3 = posRelease + v * tDelay * u
    posDetonate[2] = posRelease[2] - 0.5 * G * (tDelay**2)
    return tRelease + tDelay, posDetonate


def union_coverage(schedule):
    tStart = min(t for t, _ in schedule)
    tEnd = max(t for _, t in schedule) + tCloud
    tIterator = npy.arange(tStart, tEnd + DT, DT)
    covered = npy.zeros_like(tIterator, dtype=bool)
    for i, t in enumerate(tIterator):
        minDistance, isActive = npy.inf, False
        for tDetonate, posDetonate in schedule:
            if tDetonate <= t <= tDetonate + tCloud:
                isActive = True
                posNowMissile = getMissilePosition(t)
                posNowCloud = getCloudPosition(t, posDetonate, tDetonate)
                d = distancePoint2Line(posNowMissile, posRealTarget, posNowCloud)
                if d < minDistance:
                    minDistance = d
        covered[i] = isActive and minDistance <= rCloud

    mask = covered.astype(int)
    changes = npy.diff(mask)
    entries = tIterator[1:][changes == 1]
    exits = tIterator[1:][changes == -1]
    intervals = list(zip(entries, exits))
    tTotal = sum([end - start for start, end in intervals])
    return float(tTotal), intervals


if __name__ == "__main__":
    FIND_SCALE = 20
    best = CoverResult(-1, 0, 0, 0, 0, 0, npy.array([0.0, 0.0, 0.0]))
    results = []

    total_iterations = FIND_SCALE**4
    with tqdm(total=total_iterations, desc="Processing", unit="iteration") as pbar:
        for iTheta in npy.linspace(npy.deg2rad(175), npy.deg2rad(185), FIND_SCALE):
            for iV in npy.linspace(70, 140, FIND_SCALE):
                for iTRelease in npy.linspace(0, 1, FIND_SCALE):
                    for iTDelta in npy.linspace(2, 4, FIND_SCALE):
                        res = calculateCoverTime(iTheta, iV, iTRelease, iTDelta)
                        results.append(res)
                        if res.tCover > best.tCover:
                            best = res
                        pbar.update(1)

    # 找到 tCover 最大值对应的结果
    if results:
        best: CoverResult = max(results, key=lambda x: x.tCover)
