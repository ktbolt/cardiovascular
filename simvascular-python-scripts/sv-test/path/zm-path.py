import sv
import sv_vis as vis

print(dir(sv))

ren, renwin = vis.initRen('Test Contour')

#------------------------------------------
#             Create a path 1
#------------------------------------------
path1_name = "path1"
path1_control_points = []
path1_control_points.append([518.0, 11.0, 165.0])
path1_control_points.append([519.0, 10.0, 162.0])
#path_control_points.append([520.0, 9.0, 162.0])
path1_control_points.append([521.0, 8.0, 160.0])

path1 = sv.path.Path()
path1.new_object(path1_name)

## Set path points.
for i in range(0,len(path1_control_points)):
  path1.add_control_point(path1_control_points[i])

pt = [520.0, 9.0, 162.0]
path1.add_control_point(pt, 2)

## Create path geometry?
path1.create()
points1 = path1.get_curve_points()
control_points_1 = path1.get_control_points()
print("Control points: {0:s}".format(str(control_points_1)))

# Get path PolyData
path1_pd_name = path1_name + 'pd'
path1.get_polydata(path1_pd_name)
vis.pRepos(ren, path1_pd_name)

#------------------------------------------
#             Create a path 2
#------------------------------------------
path2_name = "path2"
path2_control_points = []
path2_control_points.append([518.0, 11.0, 165.0])
path2_control_points.append([519.0, 10.0, 162.0])
path2_control_points.append([520.0, 9.0, 162.0])
path2_control_points.append([521.0, 8.0, 160.0])

path2 = sv.path.Path()
path2.new_object(path2_name)

## Set path points.
for i in range(0,len(path2_control_points)):
  path2.add_control_point(path2_control_points[i])

## Create path geometry?
path2.create()
points2 = path2.get_curve_points()
control_points_2 = path2.get_control_points()
print("Control points: {0:s}".format(str(control_points_2)))

# Get path PolyData
path2_pd_name = path2_name + 'pd'
path2.get_polydata(path2_pd_name)
vis.pRepos(ren, path2_pd_name)


## Display the path.
##
vis.interact(ren, 1500000000)


