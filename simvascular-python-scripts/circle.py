
import math 
import numpy as np

center = np.random.uniform(low=0.5, high=13.3, size=(3))
v1 = np.random.uniform(low=0.0, high=1.0, size=(3))
v1 = v1 / np.linalg.norm(v1) 
v = np.random.uniform(low=0.0, high=1.0, size=(3))
v2 = np.cross(v1, v)
v2 = v2 / np.linalg.norm(v2) 

r = 5.0
s = r*math.sin(math.pi / 4.0)
c = r*math.cos(math.pi / 4.0)
pt = center + c*v1 + s*v2

pvec = pt - center
d = np.linalg.norm(pvec)


