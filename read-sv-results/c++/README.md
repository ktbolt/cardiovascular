
# Read SV Results

This is a C++ program used to read VTK format (.vtp and .vtu) files created by the SimVascular svSolver and svPost programs. A files is read in and the data names, mesh nodes and element connectivity, and nodal data values contained in the file are printed.

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
