import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Tuple
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm
import matplotlib.pyplot as plt

Vector3 = NDArray[npy.float64]


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
posFY2: Vector3 = npy.array([12000.0, 1400.0, 1400.0])
posFY3: Vector3 = npy.array([6000.0, -3000.0, 700.0])
speedFYMin = 70.0
speedFYMax = 140.0
G = 9.8
DT = 0.001
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

tCalculateRange = npy.arange(0.0, 100.0, DT, dtype=npy.float32)


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


@numba.jit()
def calculateCheckpoints(t: float) -> List[Vector3]:
    posNowMissile: Vector3 = getMissilePosition(t)
    # Use a Numba typed list for compatibility
    points = []
    # Manually append items from the first function call
    points_cylinder = calculateIntersection(posNowMissile)
    for p in points_cylinder:
        points.append(p)
    # Manually append items from the second function call
    points_perp = calculatePerpendicularIntersection(posNowMissile)
    for p in points_perp:
        points.append(p)
    return points


# better way to write this function
@numba.jit()
def checkLineIntersectSphere(
    linePoint1: Vector3, linePoint2: Vector3, sphereCenter: Vector3, sphereRadius: float
) -> bool:
    return distancePoint2Line(linePoint1, linePoint2, sphereCenter) <= sphereRadius


@numba.njit()
def calculateMultipleCloudTime(
    theta: float,
    speedFY: float,
    tRelease1: float,
    tDelay1: float,
    tSpan12: float,
    tDelay2: float,
    tSpan13: float,
    tDelay3: float,
) -> float:
    tReleaseList: NDArray[npy.float32] = npy.array(
        [tRelease1, tRelease1 + tSpan12, tRelease1 + tSpan13]
    )
    tDelayList: NDArray[npy.float32] = npy.array([tDelay1, tDelay2, tDelay3])
    tDetonateList: NDArray[npy.float32] = tReleaseList + tDelayList
    directionFY1: Vector3 = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    posFY1ReleaseList: NDArray[npy.float32] = npy.zeros((3, 3))
    posDetonateList: NDArray[npy.float32] = npy.zeros((3, 3))
    for i in range(3):
        posFY1ReleaseList[i, :] = posFY1 + speedFY * tReleaseList[i] * directionFY1
        posDetonateList[i, :] = (
            posFY1ReleaseList[i, :]
            + tDelayList[i] * speedFY * directionFY1
            - 0.5 * G * tDelayList[i] ** 2 * npy.array([0.0, 0.0, 1.0])
        )

    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        posMissileInstant = getMissilePosition(instant)
        checkpoints = calculateCheckpoints(instant)
        isCovered = True
        for point in checkpoints:
            isBlocked = False
            for i in range(3):
                if tDetonateList[i] <= instant <= tDetonateList[i] + tCloud:
                    posCloudInstant = getCloudPosition(
                        instant, posDetonateList[i], tDetonateList[i]
                    )
                    if checkLineIntersectSphere(
                        posMissileInstant, point, posCloudInstant, rCloud
                    ):
                        isBlocked = True
                        break
            if not isBlocked:
                isCovered = False
                break
        isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


@numba.njit()
def calculateSingleCloudTime(
    theta: float,
    speedFY: float,
    tRelease1: float,
    tDelay1: float,
) -> float:
    tDetonate = tRelease1 + tDelay1
    directionFY1: Vector3 = npy.array([npy.cos(theta), npy.sin(theta), 0.0])
    posFY1Release = posFY1 + speedFY * tRelease1 * directionFY1
    posDetonate = (
        posFY1Release
        + tDelay1 * speedFY * directionFY1
        - 0.5 * G * tDelay1**2 * npy.array([0.0, 0.0, 1.0])
    )

    isMaskedList: NDArray[npy.bool_] = npy.zeros(len(tCalculateRange), dtype=npy.bool_)
    for index, instant in enumerate(tCalculateRange):
        posMissileInstant = getMissilePosition(instant)
        checkpoints = calculateCheckpoints(instant)
        isCovered = True
        for point in checkpoints:
            isBlocked = False
            if tDetonate <= instant <= tDetonate + tCloud:
                posCloudInstant = getCloudPosition(instant, posDetonate, tDetonate)
                if checkLineIntersectSphere(
                    posMissileInstant, point, posCloudInstant, rCloud
                ):
                    isBlocked = True
            if not isBlocked:
                isCovered = False
                break
        isMaskedList[index] = 1 if isCovered else 0
    return -npy.sum(isMaskedList) * DT


def objectiveCalculateMultipleCloudTime(params):
    theta, speedFY, tRelease1, tDelay1, tSpan12, tDelay2, tSpan13, tDelay3 = params
    return calculateMultipleCloudTime(
        theta,
        speedFY,
        tRelease1,
        tDelay1,
        tSpan12,
        tDelay2,
        tSpan13,
        tDelay3,
    )


from scipy.optimize import differential_evolution

lb = [0, 70, 0, 0.1, 1, 0.1, 1, 0.1]
ub = [0.5, 140, 5, 3, 10, 3, 20, 3]
bounds = list(zip(lb, ub))

max_iterations = 500

# Set up the progress bar
pbar = tqdm(total=max_iterations, desc="Optimizing")

convergence_history = []


def callback(xk, convergence):
    t = -objectiveCalculateMultipleCloudTime(xk)
    convergence_history.append(t)
    pbar.set_postfix({"t": t})
    pbar.update(1)


result = differential_evolution(
    objectiveCalculateMultipleCloudTime,
    bounds,
    popsize=20,
    maxiter=max_iterations,
    updating="immediate",
    disp=False,
    polish=True,
    callback=callback,
    tol=DT / 10,
)

pbar.close()

print("Best parameters found:", result.x)
print("Maximum masked time:", -result.fun)

plt.figure(figsize=(10, 6))
plt.plot(range(len(convergence_history)), convergence_history)
plt.xlabel("Iteration")
plt.ylabel("Masked Time (s)")
plt.title("Differential Evolution Convergence")
plt.grid(True)
plt.show()
