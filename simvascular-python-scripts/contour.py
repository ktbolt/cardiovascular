from sv import *
import sv_vis as vis

def create_contours(path_name, control_points, radius, ren):
    print ("=============== create_contours ============")
    p = Path.pyPath()
    p.NewObject(path_name)

    ## Set path points.
    for i in range(0,len(control_points)):
        p.AddPoint(control_points[i])
    p.CreatePath()
    points = p.GetPathPosPts()
    control_points = p.GetControlPts()
    pos_pts = p.GetPathPosPts()

    ## Create circle contours at each control point.
    #
    for i in range(0,len(control_points)):
        name = path_name + "_ct" + str(i)
        print ("Create a circle Contour: " + name)
        Contour.SetContourKernel('Circle')
        c = Contour.pyContour()
        pt = control_points[i] 

        ## Find index of the point in pos_pts[] corresponding
        #  to the ith control point.
        #
        min_d = 1e9
        min_i = -1
        for j in range(0,len(pos_pts)):
          pos = pos_pts[j]
          d = sum([(pt[k]-pos[k])*(pt[k]-pos[k]) for k in range(3)])
          if (d < min_d):
            min_d = d
            min_i = j
            #__for j in range(0,len(pos_pts))
        print(">>> min_d %g  min_id %d" % (min_d, min_i))

            ## Create a contour at the min_i th pos_pts[]. 
        c.NewObject(name, path_name, min_i)

        # Set control points.
        center = control_points[i] 
        c.SetCtrlPtsByRadius(center, radius)

        # Creat contour.
        c.Create()
        print (">>> Contour center: " + str(c.Center()))

        # Get countour PolyData
        pname = name + 'p'
        c.GetPolyData(pname)
        #c.GetPolyData('ctp')
        act = vis.pRepos(ren, pname)
        #vis.polyDisplayWireframe(ren, name)

#__create_contours(path)

ren, renwin = vis.initRen('demo')

## Create a path.
control_points1 = []
control_points1.append([2.0, 2.0, 0.0])
control_points1.append([3.0, 3.0, 0.0])
control_points1.append([4.0, 4.0, 0.0])
control_points1.append([5.0, 5.0, 0.0])
radius1 = 1.0
create_contours('path1', control_points1, radius1, ren)

control_points2 = []
control_points2.append([0.0, 0.0, 0.0])
control_points2.append([0.0, 1.0, 0.0])
control_points2.append([0.0, 2.0, 0.0])
control_points2.append([0.0, 3.0, 0.0])
control_points2.append([0.0, 4.0, 0.0])
radius2 = 2.0
create_contours('path2', control_points2, radius2, ren)

## Display the contour.
##
vis.interact(ren, 1500000000)


