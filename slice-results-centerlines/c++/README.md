
# Extract SV Results from a Slice Plane along a Centerline

This is a C++ program used to interactively extract simulation results at slice planes along vessel centerlines. 
Simulation results are read from VTK format (.vtp and .vtu) files created by the SimVascular svSolver and svPost programs. 
A file is read in and the data names for the simulation results data values contained in the file are printed. The finite element
mesh is displyed and slices along a centerline can be selected using the mouse and keyboard.

## Software dependencies
The program uses cmake and vtk. 

## Building the program
To build the program:
1. $ cd **build** 
2. $ cmake ..
3. $ make

This creates an executable named **slice-results**.


## Running the program
Running the program with only a file name prints out the nodal data arrays contained in the file and displays the finite 
element mesh. You can then select elements with the mouse and display element and node IDs.

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

An element is seleted by moving the mouse over an element and pressing the **s** key. 

Exit the program by pressing the **q** key.


### Example
$ build/slice-results all_results_00100.vtp

```
File extension: vtp
Read surface mesh: all_results_00100.vtp
  Number of points: 2647
  Number of polygons: 5290
Number of point data arrays: 8
Point data array namess: 
  1: GlobalNodeID type: 6
  2: pressure type: 11
  3: velocity type: 11
  4: vinplane_traction type: 11
  5: vWSS type: 11
  6: timeDeriv type: 11
  7: average_speed type: 11
  8: average_pressure type: 11
Number of cell data arrays: 1
```

Running the program with a file name and node data name displays the finite element mesh and allows you to select elements 
with the mouse and display element and node IDs, and the simulation results at the element nodes for the specified data name.

### Example
build/slice-results all_results_00100.vtp vWSS

```
Pressed key: s
---------- Select Mesh Cell ----------
Pick position is: 1.92696 0.499054 16.9209
There are 3 points in the selection.
There are 1 cells in the selection.
Cell ID is: 4439
  Elem ID: 37652
  Number of cell points: 3
  Connectivity: 39 151 150 

Cell Data: 
  Name: vWSS
  Node ID: 39   Values: 0.0049421 -0.00728072 -1.10238
  Node ID: 151   Values: 0.00041023 -0.000378713 -1.07246
  Node ID: 150   Values: 0.00496055 -0.00203943 -1.08759
```



