# Imports
# Noise
from opensimplex import OpenSimplex
import random

#from profiling import *

# Terrain generation settings
from settings import MAX_HEIGHT

# Biome noise
def getBiomeNoise(x, y, seed):
    _x, _y = x / 1000, y / 1000
    random.seed(seed)
    n = OpenSimplex(seed=random.randint(0, 1000000))
    # Get noise layers
    noise = (n.noise2d(_x, _y) + 1) / 2 # Converting it to positive space
    # Combine them and return
    return noise

# Fractal noise
def getFractalNoise(x, y, seed):
    _x, _y = x / 10, y / 10
    n = OpenSimplex(seed=seed)
    # Get noise layers
    noise = (n.noise2d(_x, _y)) # Converting it to positive space
    random.seed(seed); n = OpenSimplex(seed=random.randint(0, 1000000))
    noise2 = (n.noise2d(_x, _y))
    n = OpenSimplex(seed=random.randint(0, 1000000))
    noise3 = (n.noise2d(_x, _y))
    n = OpenSimplex(seed=random.randint(0, 1000000))
    noise4 = (n.noise2d(_x, _y))
    # Combine them and return
    return noise + (noise2 / 2) + (noise3 / 4) + (noise4 / 8)

# Cave noise
def getCaveNoise(x, y, z, seed):
    return OpenSimplex(seed=seed).noise3d(x / 10, y / 10, z / 10)

# Get proper height data from a noise value
def getHeightFromNoise(v: float, biomeValue: float):
    # Calculate height multiplier from the biome
    m = 2
    borders = []
    if 0 < biomeValue < 0.5:
        m = 2 # Plains or very flat
        borders = [0, 0.5]
    elif 0.5 < biomeValue < 0.75:
        m = 4 # Hills
        borders = [0.5, 0.75]
    elif 0.75 < biomeValue < 0.8:
        m = 8 # Mountains
        borders = [0.75, 0.8]
    else:
        m = 16 # Super mountains
        borders = [0.8, 1.0]
    m = (m / 2) + (m * (borders[1] - borders[0]))
    r = v * m
    r += MAX_HEIGHT
    return abs(int(round(r)))
