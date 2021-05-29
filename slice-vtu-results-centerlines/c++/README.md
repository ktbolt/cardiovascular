
# Extract SV Results from a Slice Plane along a Centerline

This is a C++ program used to interactively extract simulation results at slice planes along vessel centerlines. 
Simulation results are read from VTK format (.vtu) files created by the SimVascular svSolver and svPost programs. 
The finite element mesh is displayed and slices along a centerline can be selected using the mouse.

Pressure and velocity data are extracted from the FE mesh and interpolated to the slice geometry vertices.

The centerline geometry is displayed as a green line. 

The MaximumInscribedSphereRadius at a selected centerline point is displayed as a transparent sphere. The slice is displayed as a 
red polydata. 

For a 3-button mouse
* left button is for rotation, 
* right button for zooming, 
* middle button for panning, and 
* ctrl + left button for spinning. 

## Keyboard interaction
The program is controlled using keys pressed on the keyboard. The following keys are supported

``` 
left mouse button - When positioned over a centerline creates a slice plane.
a - Extract sliceds for all centerlines poinits. 
q - Exit the program.
s - Select a centerlines point and extract a slice.
```

