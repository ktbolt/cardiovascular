The `create-sv-mesh.py` Python script is used to create the SimVascular project Models and Meshes files that allows
using a mesh in VTK VTU format created outside of SimVascular for a simulation. A SimVascular Simulations tool needs both model 
and a mesh files to execute. 

```
Usage:

  python create-sv-mesh.py FILE_NAME.vtu
```

The following files are created for an input VTK VTU named FILE_NAME.vtu 
```
  Models files:
    FILE_NAME-model.vtp - A surface with integer data arrays identifying the boundary faces
    FILE_NAME-model.mdl - An XML file defining face integer IDs with names and type (wall or cap)
       
  Meshes files:
    FILE_NAME-mesh.vtp - A surface mesh with interger data arrays identifying the boundary faces
    FILE_NAME-mesh.vtu - A volume mesh with node and element IDs 
    FILE_NAME-mesh.mdl - An XML file defining meshing parameters 
```  
Create a SimVascular project and then copy these files into the project's Models and Meshes directories. 
All faces have their type set to **wall** the the face types will need to be changed to **caps** for inlet/outlet faces.
   
Note that the mesh scale needs to match the units used in a simulation. A mesh defined too small may not display
correctly in SimVascular. A scale factor can be set to scale the mesh; see the call to the `read_mesh` function.
