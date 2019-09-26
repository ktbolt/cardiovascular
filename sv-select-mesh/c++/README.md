
# Select SV Results

This is a C++ program used to interactively select mesh elements. A surface or volume mesh can be read in from VTK 
format (.vtp and .vtu) files created by the SimVascular Mesher plugin . 

## Software dependencies
The program uses cmake and vtk. 

## Building the program
To build the program:
1. $ cd **build** 
2. $ cmake ..
3. $ make

This creates an executable named **select-meshs**.


## Running the program
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



