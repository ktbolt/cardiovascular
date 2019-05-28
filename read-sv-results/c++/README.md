
# Read SV Results

This is a C++ program used to read VTK format (.vtp and .vtu) files created by the SimVascular svSolver and svPost programs. A file is read in and the data names, mesh nodes and element connectivity, and nodal data values contained in the file are printed.

## Software dependencies
The program uses cmake and vtk. 

## Building the program
To build the program:
1. $ cd **build** 
2. $ cmake ..
3. $ make

This creates an executable named **read-results**.

## Running the program
$ build/read-results all_results_00100.vtp

```
File extension: vtp
Read polydata (.vtp) file: all_results_00100.vtp
  Number of nodes: 2647
  Number of elements: 5290
Number of node data arrays: 8
Node data arrays: 
   0: GlobalNodeID   type: int
   1: pressure   type: double
   2: velocity   type: double
   3: vinplane_traction   type: double
   4: vWSS   type: double
   5: timeDeriv   type: double
   6: average_speed   type: double
   7: average_pressure   type: double
Number of element data arrays: 1
Element data arrays: 
   0: GlobalElementID   type: int
---------- Mesh ----------
Number of coordinates: 2647
Coordinates: 
1 1  -0.696467  1.87453  14.0645
2 2  -0.391389  1.96099  13.8918
...
2646 2646  -0.0359308  0.237374  0
2647 2647  -1.6924  0.230495  30
Number of elements: 5290
Element connectivity: 
1 2  1949  2290  1952  
2 3  1604  1605  1606  
3 5  474  569  1365  
4 13  685  1857  1858  
...
5243 45700  1545  1533  1783  
5244 45701  1531  1537  1533  
5245 45702  1532  1531  1533  
---------- Mesh Data ----------
Number of node data arrays: 8
Node data array: pressure
1    132102
2    132109
3    132098
4    132112
5    132106
...
```
