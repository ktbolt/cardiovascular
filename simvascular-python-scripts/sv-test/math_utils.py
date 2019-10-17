import sv
import sv_vis as vis
import os

#help(sv.math_utils)

dy = 1.0
num_pts = 5;
points = [ [0.0, i*dy, 0.0] for i in range(0,num_pts)]
closed = False

length = sv.math_utils.curve_length(points, closed)
print("Curve length: " + str(length))

