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

## Create path geometry?
path.create()
points = path.get_curve_points()
control_points = path.get_control_points()

# Get path PolyData
path_pd_name = path_name + 'pd'
path.get_polydata(path_pd_name)
vis.pRepos(ren, path_pd_name)


#----------------------------------------------------
#                  Create Contours 
#----------------------------------------------------
# Create circle contours at each path control point.
#
radius = 1.0

for i in range(0,len(path_control_points)):
  name = path_name + "_ct" + str(i)
  print ("Create a circle Contour: " + name)
  sv.contour.set_contour_kernel('Circle')
  cont = sv.contour.Contour()
  pt = control_points[i] 
  ## Find index of the point in pos_pts[] corresponding
  #  to the ith control point.
  #
  min_d = 1e9
  min_i = -1
  for j in range(0,len(points)):
      pos = points[j]
      d = sum([(pt[k]-pos[k])*(pt[k]-pos[k]) for k in range(3)])
      if (d < min_d):
          min_d = d
          min_i = j
  #__for j in range(0,len(pos_pts))
  print(">>> min_d %g  min_id %d" % (min_d, min_i))

  ## Create a contour at the min_i th pos_pts[]. 
  cont.new_object(name, path_name, min_i)

  # Set control points.
  center = control_points[i] 
  cont.set_control_points_by_radius(center, radius)

  # Creat contour. This is not needed for circle contour.
  cont.create()
  print (">>> Contour center: " + str(cont.center()))
  print (">>> Contour area: " + str(cont.area()))

  # Get countour PolyData
  pname = name + 'p'
  cont.get_polydata(pname)
  #c.GetPolyData('ctp')
  act = vis.pRepos(ren, pname)

## Display the contour.
##
vis.interact(ren, 1500000000)


