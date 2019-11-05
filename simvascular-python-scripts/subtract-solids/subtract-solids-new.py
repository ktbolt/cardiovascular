
import sv
import sv_vis as vis

## Create a render and window to display geometry.
renderer, render_window = vis.initRen('demo')

# Set the solid modeling kernel.
sv.solid.set_kernel('PolyData')

## Read inner aorta solid model.
solid = sv.solid.SolidModel()
inner_solid_name = 'inner_aorta'
solid.read_native(inner_solid_name, 'aorta-inner.vtp')
# Create polydata to display the model.
inner_solid_pd = inner_solid_name + "_pd"
solid.get_polydata(inner_solid_pd, 1.0)
vis.pRepos(renderer, inner_solid_pd)
vis.polyDisplayWireframe(renderer, inner_solid_pd)

## Read outer aorta solid model.
solid = sv.solid.SolidModel()
outer_solid_name = 'outer_aorta'
solid.read_native(outer_solid_name, 'aorta-outer.vtp')
# Create polydata to display the model.
outer_solid_pd = outer_solid_name + "_pd"
solid.get_polydata(outer_solid_pd, 1.0)
#vis.pRepos(renderer, outer_solid_pd)
#vis.polyDisplayWireframe(renderer, outer_solid_pd)

## Subtract inner aorta from outer aorta.
wall_solid_name = 'aorta_wall'
solid.subtract(wall_solid_name, outer_solid_name, inner_solid_name)
wall_solid_pd = wall_solid_name + "_pd"
solid.get_polydata(wall_solid_pd, 1.0)
vis.pRepos(renderer, wall_solid_pd)



vis.interact(renderer, 1500000000)






