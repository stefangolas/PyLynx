# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 19:19:31 2023

@author: stefa
"""

import math

def coordinate_to_plate_idx(x,y):
    i = 84 + x - y*12
    return i

def plate_idx_to_coord(i):
    x = i%12
    y = -(i//12) + 8
    return x,y

def parabola(x, y):
    z = x**2 - 5*y**2
    return z

def shifted_parabola(x,y):
    z = (x-5)**2 + (y - 5)**2
    return z

def linear(x, y):
    z = x + y
    return z

def squared(x, y):
    z = x**2 - y
    return z

def cubic(x,y):
    z = x**3 + (y+3)**2
    return z

def oscillate(x,y):
    z = math.sin(x-4) + math.cos(y-5)
    return z

def ripples(x,y):
    r = math.sqrt((x)**2 + (y**2))
    z = math.sin(3 * r) / r
    return z

channel_data = []
xdata = []
ydata = []
zdata = []

# for i in range(96):
#     x,y = plate_idx_to_coord(i)
#     xdata.append(x)
#     ydata.append(y)
#     z = shifted_parabola(x, y)
#     channel_data.append(z)

