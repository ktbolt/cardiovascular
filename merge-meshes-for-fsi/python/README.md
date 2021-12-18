This script is used to merge .vtu and .vtp mesh files defining solid and fluid regions into a single .vtu and .vtp file.

The solid mesh is created in SV using extruded boundary layer meshing, the fluid mesh using interior boundary layer meshing.
The script removes the interior of the solid mesh using a region ID. The fluid and solid volume and surface meshes are then
merged and written to **fluid_solid_mesh.vtu** and **fluid_solid_mesh.vtp** files. 

An SV model `.mdl` file can be created by importing the **fluid_solid_mesh.vtp** file as a model into SV. Each face can then be 
named and classified as a cap or wall. 

The .vtu, .vtp, and .mdl files can then be used by the 'create-fsi-mesh-complete.py' script to create the mesh files needed
for an FSI simulation.

Usage:

```
merge-meshes.py                       \
  --fluid-mesh=FLUID_MESH             \
  --solid-mesh=SOLID_MESH             \
  --solid-region-id=SOLID_REGION_ID

  where

      FLUID_MESH - The name of the fluid .vtu and .vtp files.

      SOLID_MESH - The name of the solid .vtu and .vtp files.

      SOLID_REGION_ID - The solid region ID (usually 2)

```

