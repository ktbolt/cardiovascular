
import sys
import sv
import sv_vis as vis

## Create a render and window to display geometry.
renderer, render_window = vis.initRen('demo')

# Set the solid modeling kernel.
sv.Solid.SetKernel('PolyData')

## Read inner aorta solid model.
solid = sv.Solid.pySolidModel()
inner_solid_name = 'inner_aorta'
solid.ReadNative(inner_solid_name, 'aorta-inner.vtp')

# Create polydata to display the model.
inner_solid_pd = inner_solid_name + "_pd"
solid.GetPolyData(inner_solid_pd, 1.0)
#vis.pRepos(renderer, inner_solid_pd)

## Read outer aorta solid model.
solid = sv.Solid.pySolidModel()
outer_solid_name = 'outer_aorta'
solid.ReadNative(outer_solid_name, 'aorta-outer.vtp')
# Create polydata to display the model.
outer_solid_pd = outer_solid_name + "_pd"
solid.GetPolyData(outer_solid_pd, 1.0)
#vis.pRepos(renderer, outer_solid_pd)
#vis.polyDisplayWireframe(renderer, outer_solid_pd)

## Subtract inner aorta from outer aorta.
wall_solid_name = 'subtract_inner_outer_aorta'
solid.Subtract(wall_solid_name, outer_solid_name, inner_solid_name)
wall_solid_pd = wall_solid_name + '_pd'
solid.GetBoundaryFaces(80)
print ("Model face IDs: " + str(solid.GetFaceIds()))
solid.GetPolyData(wall_solid_pd, 0.1)
vis.pRepos(renderer, wall_solid_pd)

# Write the wall model.
solid.WriteNative('aorta-wall.vtp')

vis.interact(renderer, sys.maxsize)


