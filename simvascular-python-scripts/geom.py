from sv import *
import sv_vis as vis
import random, os

# ##############################################################################
# This script is a demo of the various features offered by the Geom.xyz API set.
# Some demos use a simple intersecting pair of hollow cylinders, while others
# make use of a simple 1 x 1 x 1 cube so as to make comprehension of the output
# format and content easier.
# ##############################################################################

#
# Creates a lofted surface from the provided source path with circular contours
# with radii +/- little value from initial_radius.
#
# Args:
#  src_path_name (String): Name of the source path.
#  initial_radius (double): Initial "average" radius to use.
# Returns:
#  String: Name of the resulting lofted solid.

def create_surface_from_path(src_path_name, initial_radius):
    # Load in the source path and store the position points.
    path = Path.pyPath()
    path.GetObject(src_path_name)
    path_pos_points = path.GetPathPosPts()

    # Create contours from the points.
    kernel = "Circle"
    Contour.SetContourKernel(kernel)

    prev_radius = initial_radius # Last radius from which to add/subtract a random number.
    path_ctr_pds = []            # List of polydata objects created from the contours.
    # Extract every 10'th contour.
    for id in range(int(path.GetPathPtsNum() / 10)):
        contour = Contour.pyContour()

        # Create a new blank contour object.
        path_contour_name = src_path_name + "-contour" + str(id * 10)
        create_from_point = id * 10
        contour.NewObject(path_contour_name, src_path_name, create_from_point)

        # Randomize the radius and create the circular contour. Coords for the
        # center must be defined in absolute 3D space, so we must grab the real
        # position point from the path data.
        center_pt = path_pos_points[create_from_point]
        radius = prev_radius + 0 * (random.random() - 0.5)
        prev_radius = radius
        contour.SetCtrlPtsByRadius(center_pt, radius)

        # Extract a polydata object from the created contour and save its name in the list.
        pd_path_name = path_contour_name + "-pd"
        path_ctr_pds.append(pd_path_name)
        contour.GetPolyData(pd_path_name)

    # Resample the contour polydata objects.
    num_samples = 60  # Number of samples to take around circumference of contour?
    path_ctrs_pds_rspl = []
    for id in path_ctr_pds:
        new_id = id + "_resampled"
        path_ctrs_pds_rspl.append(new_id)
        Geom.SampleLoop(id, num_samples, new_id)

    # Loft the resampled contours.
    path_lofted_name = src_path_name + "_lofted"
    num_contours = len(path_ctrs_pds_rspl) * 4  # Including endpoints, how many contours to interpolate between the end caps.
    num_linear_pts_along_length = 120           # ?
    num_modes = 20                              # ?
    use_FFT = 0                                 # ?
    use_linear_sample_along_length = 1          # Linearly interpolate the contours see num_contours_to_loft.
    Geom.LoftSolid(path_ctrs_pds_rspl, path_lofted_name, num_samples,
                  num_contours, num_linear_pts_along_length, num_modes,
                  use_FFT, use_linear_sample_along_length)

    return path_lofted_name

#
# Initialize the first path.
#

# Create new path object.
path1_name = "path1"
path1 = Path.pyPath()
path1.NewObject(path1_name)

# Give it some points.
path1.AddPoint([2.0, 2.0, 0.0])
path1.AddPoint([3.0, 3.0, 0.0])
path1.AddPoint([4.0, 4.0, 0.0])
path1.AddPoint([5.0, 5.0, 0.0])
# Generate the path from the added control points.
path1.CreatePath()

#
# Initialize the second path.
#

# Create new path object.
path2_name = "path2"
path2 = Path.pyPath()
path2.NewObject(path2_name)

# Give it some points.
path2.AddPoint([0.0, 0.0, 0.0])
path2.AddPoint([0.0, 1.0, 0.0])
path2.AddPoint([0.0, 2.0, 0.0])
path2.AddPoint([0.0, 3.0, 0.0])
path2.AddPoint([0.0, 4.0, 0.0])
# Generate the path from the added control points.
path2.CreatePath()

# Create surfaces from the paths.
path1_surface_name = create_surface_from_path(path1_name, 1.0)
path2_surface_name = create_surface_from_path(path2_name, 2.0)

path1_cap_surface_name = path1_surface_name + "_capped"
VMTKUtils.Cap_with_ids(path1_surface_name, path1_cap_surface_name, 0, 0)

path2_cap_surface_name = path2_surface_name + "_capped"
VMTKUtils.Cap_with_ids(path2_surface_name, path2_cap_surface_name, 0, 0)


Solid.SetKernel('PolyData')

merged_solid_name_pd = "merged_solid"
#Geom.Union(path1_cap_surface_name, path2_cap_surface_name, merged_solid_name_pd)
Geom.Union(path1_surface_name, path2_surface_name, merged_solid_name_pd)
print("Surf Area:")
print(str(Geom.SurfArea(merged_solid_name_pd)))


print("\n[geom_stats_demo] Geom.All_union()")
inter_t = True
destination_name = merged_solid_name_pd + "_merged_again"
#result = Geom.All_union([path1_cap_surface_name, path2_cap_surface_name], inter_t, destination_name)
#print(">>> result " + str(result))

intersected_solid_name = "intersect"
#Geom.Intersect(path1_surface_name, path2_surface_name, intersected_solid_name)
#Geom.Intersect(path1_cap_surface_name, path2_cap_surface_name, intersected_solid_name)


# Render this all to a viewer.
window_name = 'contour_to_lofted_model.py'
ren, renwin = vis.initRen(window_name)

actor1 = vis.pRepos(ren, path1_cap_surface_name)
#actor1 = vis.pRepos(ren, path1_surface_name)

actor2 = vis.pRepos(ren, path2_cap_surface_name)
#actor2 = vis.pRepos(ren, path2_surface_name)

#actor3 = vis.pRepos(ren, destination_name)
actor3 = vis.pRepos(ren, merged_solid_name_pd)
#actor3 = vis.pRepos(ren, intersected_solid_name)

# Set the renderer to draw the solids as a wireframe.
vis.polyDisplayWireframe(ren, path1_cap_surface_name)
vis.polyDisplayWireframe(ren, path2_cap_surface_name)

vis.interact(ren, 15000)



