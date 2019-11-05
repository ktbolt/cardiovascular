import sv
import sv_vis as vis

print(dir(sv))

ren, renwin = vis.initRen('Test Contour')

#------------------------------------------
#             Create a path
#------------------------------------------
path_name = "path1"
path_control_points = []
path_control_points.append([2.0, 2.0, 0.0])
path_control_points.append([3.0, 3.0, 0.0])
path_control_points.append([4.0, 4.0, 0.0])
path_control_points.append([5.0, 5.0, 0.0])

path = sv.path.Path()
path.new_object(path_name)

## Set path points.
for i in range(0,len(path_control_points)):
  path.add_control_point(path_control_points[i])

pt = [5.0, 5.5, 0.0]
path.add_control_point(pt)

## Create path geometry?
path.create()
points = path.get_curve_points()
control_points = path.get_control_points()
print("Control points: {0:s}".format(str(control_points)))

# Get path PolyData
path_pd_name = path_name + 'pd'
path.get_polydata(path_pd_name)
vis.pRepos(ren, path_pd_name)


## Display the path.
##
vis.interact(ren, 1500000000)


