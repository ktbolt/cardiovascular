
# Extract SV Results from a Slice Plane along a Centerline

This is a C++ program used to interactively extract simulation results at slice planes along vessel centerlines. 
Simulation results are read from VTK format (.vtp) files created by the SimVascular svSolver and svPost programs. 
A file is read in and the data names for the simulation results data values contained in the file are printed. The finite element mesh is displayed and slices along a centerline can be selected using the mouse.

The centerline geometry is displayed as a green line, the finite element surface is displayed as a transparent gray surface.
The intersection of a slice plane with a vessel is displayed as 1) a planar greometry (red) representing the vessel cross sectional area at the slice location and 2) the points where the slice intersects the finite element mesh (yellow markers). 

<img style="margin:0px auto;display:block" src="images/slice-geometry.png" />

Simulation results are interpolated at the yellow markers and written to a file. The file contains the interpolated data for each slice, slice area and the coordinates of the interpolation points.

```
# Slices file
data name: pressure
number of slices: 3

slice 1
area: 5.45798
centerline index: 646
centerline cell ID: 0
centerline point: -0.0255586 0.00669105  6.02712
points:
-1.26892 0.462231  6.06333
-1.22665 0.585386  6.08827
-1.20881 0.625086  6.09648
-1.16865 0.714586  6.11499
-1.12606 0.78755  6.13047
...
data:
798885
798890
798905
798923
798913
...

slice 2
area: 3.34477
centerline index: 557
centerline cell ID: 0
centerline point: -0.018745 0.586371  2.74516
points:
0.936616 0.990295  2.73022
0.949155 0.955118  2.72365
0.982967 0.861774  2.70617
```

## Software dependencies
The program uses cmake and vtk. 

## Building the program
To build the program:
1. $ cd **cardiovascular/slice-results-centerlines/c++**
2. $ mkdir **build**
3. $ cd **build** 
4. $ cmake ..
5. $ make

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
The program is controlled using keys pressed on the keyboard. The following keys are supported

``` 
left mouse button - When positioned over a centerline creates a slice plane.
q - Exit the program.
u - Remove last slice.
w - Write slices to a file.
```

### Example
Process a results file for the Demo project
```
$ build/slice-results all_results_00100.vtp demo_cl.vtp pressure
```

This reads in the file and prints the names of the data in the results file

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
Now select three slices

<img style="margin:0px auto;display:block" src="images/slice-example.png" />

Write the results to **all_results_0010_pressure.txt**.


