import sys
import numba
import numba.cuda
from numpy.typing import NDArray
import numpy as npy
from typing import List, Optional, Tuple
from scipy.optimize._optimize import OptimizeResult
from tqdm import tqdm
from sko.GA import GA

Vector3 = NDArray[npy.float64]


posMissile1: Vector3 = npy.array([20000.0, 0.0, 2000.0])
posMissile2: Vector3 = npy.array([19000.0, 600.0, 2100.0])
posMissile3: Vector3 = npy.array([18000.0, -600.0, 1900.0])
speedMissile = 300.0
posMissileTarget: Vector3 = npy.array([0.0, 0.0, 0.0])
directionMissile1: Vector3 = (posMissileTarget - posMissile1) / npy.linalg.norm(
    posMissileTarget - posMissile1
)
vMissile1 = speedMissile * directionMissile1
directionMissile2: Vector3 = (posMissileTarget - posMissile2) / npy.linalg.norm(
    posMissileTarget - posMissile2
)
vMissile2 = speedMissile * directionMissile2
directionMissile3: Vector3 = (posMissileTarget - posMissile3) / npy.linalg.norm(
    posMissileTarget - posMissile3
)
vMissile3 = speedMissile * directionMissile3
posRealTarget: Vector3 = npy.array([0.0, 200.0, 0.0])
posFakeTarget = posMissileTarget
rRealTarget = 7
hRealTarget = 10
posFY1: Vector3 = npy.array([17800.0, 0.0, 1800.0])
posFY2: Vector3 = npy.array([12000.0, 1400.0, 1400.0])
posFY3: Vector3 = npy.array([6000.0, -3000.0, 700.0])
posFY4: Vector3 = npy.array([11000.0, 2000.0, 1800.0])
posFY5: Vector3 = npy.array([13000.0, -2000.0, 1300.0])
speedFYMin = 70.0
speedFYMax = 140.0
G = 9.8
DT = 0.02
rCloud = 10.0
speedCloud = 3.0
tCloud = 20.0

tCalculateRange = npy.arange(0.0, 100.0, DT, dtype=npy.float32)
