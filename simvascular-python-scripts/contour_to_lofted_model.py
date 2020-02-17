from sv import *
import sv_vis as vis
import random, os

def create_solid_from_path(src_path_name, starting_radius):
    path_name = src_path_name
    path = Path.pyPath()
    path.GetObject(path_name)
    pos_points = path.GetPathPosPts()

    # Create contours from the points.
    kernel = 'Circle'
    Contour.SetContourKernel(kernel)

    prev_radius = starting_radius # Last radius from which to add/subtract a random number.
    path_ctr_pds = []             # List of polydata objects created from the contours.
    # Extract every 10'th contour.
    for id in range(int(path.GetPathPtsNum() / 10)):
        contour = Contour.pyContour()

        # Create a new blank contour object.
        path_contour_name = path_name + '-contour' + str(id * 10)
        create_from_path_point = id * 10
        contour.NewObject(path_contour_name, path_name, create_from_path_point)

        # Randomize the radius and create the circular contour.
        #center_pt = [0, 0, 0]
        center_pt = pos_points[create_from_path_point]
        radius = prev_radius + 5* (random.random() - 0.5)
        prev_radius = radius
        contour.SetCtrlPtsByRadius(center_pt, radius)

        # Extract a polydata object from the created contour and save its name in the list.
        pd_path_name = path_contour_name + "-pd"
        path_ctr_pds.append(pd_path_name)
        contour.GetPolyData(pd_path_name)

    # Resample the contour polydata objects.
    num_samples = 60  # Number of samples to take around circumference of contour?
    num_samples = 20  # Number of samples to take around circumference of contour?
    path_ctrs_pds_rspl = []
    for id in path_ctr_pds:
        new_id = id + "_resampled"
        path_ctrs_pds_rspl.append(new_id)
        Geom.SampleLoop(id, num_samples, new_id)

    # Loft the resampled contours.
    path_lofted_name = path_name + "_lofted"
    num_contours = len(path_ctrs_pds_rspl) * 4  # Including endpoints, how many contours to interpolate between the end caps.
    num_linear_pts_along_length = 120           # ?
    num_modes = 20                              # ?
    use_FFT = 0                                 # ?
    use_linear_sample_along_length = 1          # Linearly interpolate the contours see num_contours_to_loft.
    Geom.LoftSolid(path_ctrs_pds_rspl, path_lofted_name, num_samples,
                  num_contours, num_linear_pts_along_length, num_modes,
                  use_FFT, use_linear_sample_along_length)

    # Create a new solid from the lofted solid.
    Solid.SetKernel('PolyData')
    solid = Solid.pySolidModel()
    path_solid_name = path_name + "_solid"
    solid.NewObject(path_solid_name)
    # Cap the lofted volume.
    path_lofted_capped_name = path_lofted_name + "_capped"
    VMTKUtils.Cap_with_ids(path_lofted_name, path_lofted_capped_name, 0, 0)
    solid.SetVtkPolyData(path_lofted_capped_name)
    num_triangles_on_cap = 150
    solid.GetBoundaryFaces(num_triangles_on_cap)

    # Export the solid to a polydata object.
    path_solid_pd_name = path_solid_name + "_pd"
    solid.GetPolyData(path_solid_pd_name)

    # solid.WriteNative(os.getcwd() + "/" + path_solid_name + ".vtp")

    return path_solid_pd_name

# Create new path object.
path1_name = 'path1'
path1 = Path.pyPath()
path1.NewObject(path1_name)

# Give it some points.
path1.AddPoint([0.0, 0.0, 0.0])
path1.AddPoint([0.0, 0.0, 10.0])
path1.AddPoint([0.0, 0.0, 20.0])
path1.AddPoint([1.0, 0.0, 30.0])
path1.AddPoint([0.0, 0.0, 40.0])
path1.AddPoint([0.0, 0.0, 50.0])
path1.AddPoint([0.0, 0.0, 60.0])
# Generate the path from the added control points.
path1.CreatePath()

# Create new path object.
path2_name = 'path2'
path2 = Path.pyPath()
path2.NewObject(path2_name)

# Give it some points.
path2.AddPoint([0.0, 100.0, 0.0])
path2.AddPoint([0.0, 100.0, 10.0])
path2.AddPoint([0.0, 100.0, 20.0])
path2.AddPoint([1.0, 100.0, 30.0])
path2.AddPoint([0.0, 100.0, 40.0])
path2.AddPoint([0.0, 100.0, 50.0])
path2.AddPoint([0.0, 100.0, 60.0])
# Generate the path from the added control points.
path2.CreatePath()

# Create solids from the paths.
path1_solid_name = create_solid_from_path(path1_name, 5.0)
path2_solid_name = create_solid_from_path(path2_name, 5.0)

# Render this all to a viewer.
window_name = 'contour_to_lofted_model.py'
ren, renwin = vis.initRen(window_name)
actor1 = vis.pRepos(ren, path1_solid_name)
actor2 = vis.pRepos(ren, path2_solid_name)
# Set the renderer to draw the solids as a wireframe.
#vis.polyDisplayWireframe(ren, path1_solid_name)
#vis.polyDisplayWireframe(ren, path2_solid_name)

vis.interact(ren, 15000)
