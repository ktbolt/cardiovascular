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
path2_cap_surface_name = path2_surface_name + "_capped"
VMTKUtils.Cap_with_ids(path1_surface_name, path1_cap_surface_name, 0, 0)
VMTKUtils.Cap_with_ids(path2_surface_name, path2_cap_surface_name, 0, 0)

merged_solid_name_pd = "merged_solid"
# Geom.Union(path1_surface_name, path2_surface_name, merged_solid_name_pd)
Geom.Union(path1_cap_surface_name, path2_cap_surface_name, merged_solid_name_pd)

#
# Initialize alternate cube testing platform.
#

cube_name = "cube"
cube_name_pd = cube_name + "_pd"
cube_size = [1.0, 1.0, 1.0]
cube_center = [0.0, 0.0, 0.0]
Solid.SetKernel('PolyData')
cube = Solid.pySolidModel()
cube.Box3d(cube_name, cube_size, cube_center)
cube.GetPolyData(cube_name_pd)

# ######################################
#           BEGIN GEOM API DEMO
# ######################################

# ERR: VtkUtils_GetLines failed ?
# print("\n[geom_stats_demo] Geom.NumClosedLineRegions()")
# # result = Geom.NumClosedLineRegions(merged_solid_name_pd)
# result = Geom.NumClosedLineRegions(cube_name_pd)
# print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.Translate()")
translate_vec = [1.0, 2.0, 3.0]
translated_solid_name = merged_solid_name_pd + "_translated"
Geom.Translate(merged_solid_name_pd, translate_vec, translated_solid_name)

print("\n[geom_stats_demo] Geom.ScaleAvg()")
scale_factor = 2.0
scaled_solid_name = merged_solid_name_pd + "_scaled"
Geom.ScaleAvg(merged_solid_name_pd, scale_factor, scaled_solid_name)

# ERR: VtkUtils_GetLines failed ?
# print("\n[geom_stats_demo] Geom.GetOrderedPts()")
# # result = Geom.GetOrderedPts(merged_solid_name_pd)
# result = Geom.GetOrderedPts(cube_name_pd)
# print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.PolysClosed()")
result = Geom.PolysClosed(cube_name_pd)
print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.SurfArea()")
result = Geom.SurfArea(cube_name_pd)
print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.PrintTriStats()")
Geom.PrintTriStats(merged_solid_name_pd)

print("\n[geom_stats_demo] Geom.PrintSmallPolys()")
min_edge_size = 0.1
Geom.PrintSmallPolys(merged_solid_name_pd, min_edge_size)

print("\n[geom_stats_demo] Geom.Bbox()")
result = Geom.Bbox(cube_name_pd)
print("[geom_stats_demo] \tResult: (x1, y1, z1, x2, y2, z2) " + str(result))

print("\n[geom_stats_demo] Geom.Classify()")
point = [0.0, 0.0, 0.0]
result = Geom.Classify(merged_solid_name_pd, point)
print("[geom_stats_demo] \tResult: " + str(result))

# TODO(Dave or other): SolidModel.GetRegionIds() relies on an unimplemented function.
# RR: sys_geom_Get2DPgon called with non-planar input cvPolyData ?
# print("\n[geom_stats_demo] Geom.PtInPoly()")
# cube.GetRegionIds()
# faces_list = cube.GetFaceIds()
# print("faces_list:")
# print(faces_list)
# face_pd_name = "cube_face"
# cube.GetFacePolyData(face_pd_name, faces_list[0])

# point = [0.0, 0.0]
# use_previous_polygon = False
# result = Geom.PtInPoly(face_pd_name, point, use_previous_polygon)
# print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.NumPts()")
result = Geom.NumPts(merged_solid_name_pd)
print("[geom_stats_demo] \tResult: " + str(result))

# TODO(Dave or other): 2dWindingNum isn't a valid keyword name. Python API is broken.
# print("\n[geom_stats_demo] Geom.2dWindingNum()")
# result = Geom.2dWindingNum(merged_solid_name)
# print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.AvgPt()")
result = Geom.AvgPt(cube_name_pd)
print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.FindDistance()")
point = [0.0, 0.0, 0.0]
result = Geom.FindDistance(merged_solid_name_pd, point)
print("[geom_stats_demo] \tResult: " + str(result))

print("\n[geom_stats_demo] Geom.Checksurface()")
result = Geom.Checksurface(merged_solid_name_pd)
print("[geom_stats_demo] \tResult: (num free edges, num bad edges) " + str(result))

print("\n[geom_stats_demo] Geom.Clean()")
cleaned_name = merged_solid_name_pd + "_cleaned"
Geom.Clean(merged_solid_name_pd, cleaned_name)

# Sometimes errors out with: "current kernel is not valid (6)" ?
print("\n[geom_stats_demo] Geom.All_union()")
inter_t = True
destination_name = merged_solid_name_pd + "_merged_again"
result = Geom.All_union([path1_surface_name, path2_surface_name], inter_t, destination_name)

print("\n[geom_stats_demo] Geom.Intersect()")
intersected_solid_name = "intersected_solid"
Geom.Intersect(merged_solid_name_pd, cube_name_pd, intersected_solid_name)
# TODO(Neil): Figure out how to visualize this model. How to get it into a solid model object?
window_name = "INTERSECTED Model"
ren1, renwin1 = vis.initRen(window_name)
actor1 = vis.pRepos(ren1, intersected_solid_name)
# Set the renderer to draw the solids as a wireframe.
vis.polyDisplayWireframe(ren1, intersected_solid_name)

print("\n[geom_stats_demo] Geom.Subtract()")
subtracted_solid_name = "subtracted_solid"
Geom.Subtract(merged_solid_name_pd, cube_name_pd, subtracted_solid_name)
# TODO(Neil): Figure out how to visualize this model. How to get it into a solid model object?
window_name = "SUBTRACTED Model"
ren2, renwin2 = vis.initRen(window_name)
actor2 = vis.pRepos(ren2, subtracted_solid_name)
# Set the renderer to draw the solids as a wireframe.
vis.polyDisplayWireframe(ren2, subtracted_solid_name)

vis.interact(ren1, 15000)
vis.interact(ren2, 15000)
