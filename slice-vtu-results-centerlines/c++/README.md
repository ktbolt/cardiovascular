
# Extract SV Results from a Slice Plane along a Centerline

This is a C++ program used to interactively extract simulation results at slice planes along vessel centerlines. 
Simulation results are read from VTK format (.vtu) files created by the SimVascular svSolver and svPost programs. 
The finite element mesh is displayed and slices along a centerline can be selected using the mouse.

The centerline geometry is displayed as a green line. 

A slice is extracted on a plane defined by a centerline point and normal data. A distance scalar field is created 
for the FE mesh containing the distance from that point to the plane. The vtkContourGrid method is then
used to extract a zero-level isosurface from the distance scalar field. Pressure and velocity data from the FE mesh 
is also interpolated to the isosurface geometry vertices.

Computing the distance scalar field is fast and the marching cubes algorithm used by vtkContourGrid has O(n) complexity, 
where n = the number of elements in the FE mesh, so the method is quite efficient. Slices have been extracted for a 
70,665 element mesh for all 1,184 centerline points in about 20 seconds (2.9GHz processor).

The MaximumInscribedSphereRadius at a selected centerline point is displayed as a transparent sphere. The slice is displayed as a 
red polydata. 

A slice is by default trimmed to the incribed sphere radius from the centerline data. Trimming can be toggled using the
't' key.

For a 3-button mouse
* left button is for rotation, 
* right button for zooming, 
* middle button for panning, and 
* ctrl + left button for spinning. 

## Keyboard interaction
The program is controlled using keys pressed on the keyboard. The following keys are supported

``` 
a - Extract slices for all centerlines points 
q - Exit the program
s - Select a centerlines point and extract a slice at the current mouse position
t - Toggle trimming a slice using an incribed sphere radius
```

