import sv
import sv_vis as vis
import os

## Create a render and window to display geometry.
renderer, render_window = vis.initRen('demo')

surf_name = "shapeSnakeDiaSmooth"
surf_file_name = surf_name + ".vtp"

## Create a solid model from polydata.
#
sv.solid.set_kernel('PolyData')
solid = sv.solid.SolidModel()

# Read surface polydata.
solid.read_native(surf_name, surf_file_name)

## Display surface.
surf_pd = surf_name + "_pd"
solid.get_polydata(surf_pd, 1.0)
vis.pRepos(renderer, surf_pd)
vis.polyDisplayWireframe(renderer, surf_pd)

## Cap the surface.
capped_surf_name = surf_name + "_capped"
sv.VMTKUtils.Cap_with_ids(surf_pd, capped_surf_name, 0, 0)
sv.Repository.WriteVtkPolyData(capped_surf_name, 'binary', capped_surf_name+".vtp")
vis.pRepos(renderer, capped_surf_name)

vis.interact(renderer, 1500000000)



