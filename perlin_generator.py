import numpy as np
import math
from random import shuffle

vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])

def lerp(a, b, x):
    #dot product
    return a + x * (b-a)

def fade(x):
    #This is the formula used to smooth perlin noise
    return 6 * x**5 - 15 * x**4 + 10 * x**3

def gradient(c, x, y):
    return vectors[c%4]*x + vectors[c%4]*y

def perlin(x,y,seed=0):
    #Create Pivot table
    np.random.seed(seed)
    permutable = np.arange(256, dtype=int)
    shuffle(permutable)

    #grid coordinates
    xi, yi = int(math.floor(x)), int(math.floor(y))
   
    # distance vector coordinates
    xg, yg = x - xi, y - yi
    
    # apply fade function to distance coordinates
    xf, yf = fade(xg), fade(yg)
    
    # the gradient vector coordinates in the top left, top right, bottom left bottom right
    try:
        n00 = gradient(permutable[permutable[xi] + yi], xg, yg)
        n01 = gradient(permutable[permutable[xi] + yi + 1], xg, yg - 1)
        n11 = gradient(permutable[permutable[xi + 1] + yi + 1], xg - 1, yg - 1)
        n10 = gradient(permutable[permutable[xi + 1] + yi], xg - 1, yg)
    except Exception:
        n00 = 0
        n01 = 0
        n11 = 0
        n10 = 0
    
    # apply linear interpolation i.e dot product to calculate average
    x1 = lerp(n00, n10, xf)
    x2 = lerp(n01, n11, xf)  
    return lerp(x1, x2, yf)  
