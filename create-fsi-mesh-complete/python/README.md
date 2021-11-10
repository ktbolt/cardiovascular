# create-fsi-mesh-complete.py

The **create-fsi-mesh-complete.py** script is used to create the mesh-complete files needed to run svFSI simulations from the .vtu and .vtp files 
created by the SV Meshing tool. A boundary layer mesh is required with region IDs; this is enabled by checking the SV 
**Convert Boundary Layer to New Region/Domain** option. Fluid elements are identified using region ID 1, solid elements region ID 2.

A model .mdl file is used to identify each face with its ID, name, and type (wall or cap). 
This is the model referenced in the SV Meshing tool. The mesh surface .vtp file contains 
`ModelFaceID` CellData that identifies the mesh faces and `GlobalElementID` CellData that 
identifies elements.

The solid mesh will have both inner and outer components. The inner solid mesh face interfaces 
to the fluid wall face(s).

Files are written for each fluid and solid volume mesh, and the faces for each used to specify boundary
conditions. The file naming convention is

```
  solid-mesh.vtu                
  solid-CAP_FACE_NAME1.vtp      
  solid-CAP_FACE_NAME2.vtp      
  ...
  solid-WALL_FACE_NAME1-inner.vtp       
  solid-WALL_FACE_NAME1-outer.vtp       
  solid-WALL_FACE_NAME2-inner.vtp       
  solid-WALL_FACE_NAME2-outer.vtp       
  ...
  fluid-mesh.vtu
  solid-CAP_FACE_NAME1.vtp      
  solid-CAP_FACE_NAME2.vtp      
```

Usage: 

  create-fsi-mesh-complete.py  
      --fluid-region-id FLUID_REGION_ID 
      --mdl-file MDL_FILE 
      --solid-region-id SOLID_REGION_ID 
      --surface-mesh SURFACE_MESH 
      --volume-mesh VOLUME_MESH

  where

      FLUID_REGION_ID - The fluid region ID (usually 1)

      MDL_FILE - The SV modeling .mdl file    

      SOLID_REGION_ID - The solid region ID (usually 2)

      SURFACE_MESH - The surface mesh (.vtp) file.

      VOLUME_MESH - The volume mesh (.vtu) file.


