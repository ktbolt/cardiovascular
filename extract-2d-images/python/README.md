
# Extract 2D Images from an Image Volume

This Python code is used to extract 2D slices from a 3D image volume and surface geometry using VTK.
Slices are extracted using data along a SimVascular path (position, tangent and normal to a path line)
to define a plane for slicing. A SimVascular model given in a .vtp file is also sliced at a given path 
position. The image and model slices are written to VTK .vti and .vtp files.

A set of interpolating points created on the slice plane are used to sample the image volume. The spacing
of the interpolation points is set to min(image spacing) / 2.0.

Image slices data are written to files named image_slice_PATH_POINT_ID.vti

Model slices data are written to files named model_slice_PATH_POINT_ID.vti

PATH_POINT_ID is the the value of each path point id given in the .pth file. 

```
  <path_point id="1">
    <pos x="-2.24355483017504" y="-2.03100002186194" z="13.535332348831323" />
    <tangent x="0.459604696925632" y="0.399318918662815" z="-0.793289306471389" />
    <rotation x="0" y="0.89321949067228" z="0.449620886395586" />
  </path_point>
```

Path, model, and image slices can be displayed in a graphics window. A slice can be created interactively by moving the mouse cursor over a path location and pressing the **s** key. 

Usage: extact-2d-images.py [-h] [--enable-graphics ENABLE_GRAPHICS] [--extract-slices EXTRACT_SLICES] [--image-file-name IMAGE_FILE_NAME]
                           [--model-file-name MODEL_FILE_NAME] [--path-file-name PATH_FILE_NAME] [--results-directory RESULTS_DIRECTORY]
                           [--slice-increment SLICE_INCREMENT] [--slice-width SLICE_WIDTH]

  ENABLE_GRAPHICS - Enable graphics to show geomemtry in a graphics window.

  EXTRACT_SLICES  - Automatically extract slices using the slice increment.

  IMAGE_FILE_NAME - The image volume (.vti) file.

  MODEL_FILE_NAME - The SV model (.vtp) file.

  PATH_FILE_NAME - The SV path (.pth) file.

  RESULTS_DIRECTORY - The directory to write image and model slice files.

  SLICE_INCREMENT - The slice increment along a path.

  SLICE_WIDTH - The width of a slice plane.


Example: Automatically extracting all slices every 50 path points. 

    python extact-2d-images.py     \
        --image-file aorta.vti     \
        --path-file aorta.pth      \
        --model-file demo.vtp      \
        --slice-increment 50       \
        --slice-width 5            \
        --extract-slices true      \
        --results-directory ./results \
        --enable-graphics true


