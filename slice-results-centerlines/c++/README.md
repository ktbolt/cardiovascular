
# Extract SV Results from a Slice Plane along a Centerline

This is a C++ program used to interactively extract simulation results at slice planes along vessel centerlines. 
Simulation results are read from VTK format (.vtp) files created by the SimVascular svSolver and svPost programs. 
A file is read in and the data names for the simulation results data values contained in the file are printed. The finite element mesh is displayed and slices along a centerline can be selected using the mouse.

## Software dependencies
The program uses cmake and vtk. 

## Building the program
To build the program:
1. $ cd **build** 
2. $ cmake ..
3. $ make

This creates an executable named **slice-results**.


## Running the program
The program is executing using
```
build/slice-results  SVSOLVERFILE.vtp   CENTERLINEFILE.vtp  DATANAME
```
Running the program with only a simulation results file name prints out the nodal data arrays contained in the file and exits. 

## Graphics interface
The program uses a trackball camera to interactively manipulate (rotate, pan, etc.) the camera, the viewpoint of the scene.
For a trackball interaction the magnitude of the mouse motion is proportional to the camera motion associated with a 
particular mouse key. For example, small left-button motions cause small changes in the rotation of the camera 
around its focal point. 

For a 3-button mouse
* left button is for rotation, 
* right button for zooming, 
* middle button for panning, and 
* ctrl + left button for spinning. 

With fewer mouse buttons, ctrl + shift + left button is for zooming, and shift + left button is for panning.)

## Keyboard interaction
The program is controled using keys pressed on the keyboard. The following keys are supported

``` 
left mouse button - When positioned over a centerline creates a slice plane.
q - Exit the program.
w - Write slices to a file.
```

### Example
$ build/slice-results all_results_00100.vtp demo_cl.vtp pressure

``` 
File extension: vtp
File prefix: all_results_0010
Read surface mesh: all_results_00100.vtp
  Number of points: 13711
  Number of polygons: 27418
Surface point data arrays: 8
  Number of point data arrays: 8
  Point data array namess: 
    1: GlobalNodeID type: 6  numComp: 1
    2: vinplane_traction type: 11  numComp: 3
    3: vWSS type: 11  numComp: 3
    4: average_speed type: 11  numComp: 1
    5: average_pressure type: 11  numComp: 1
    6: pressure type: 11  numComp: 1
    7: velocity type: 11  numComp: 3
    8: timeDeriv type: 11  numComp: 4
  Number of cell data arrays: 1
Read centerlines: demo_cl.vtp
Number of vertices 1466
Number of lines 2
Number of PointData arrays: 3
PointData arrays: 
Have MaximumInscribedSphereRadius data

```


