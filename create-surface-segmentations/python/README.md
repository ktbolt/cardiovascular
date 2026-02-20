This directory contains the Python create_surface_segmentations.py scripts used to create slices of a surface geometry along 
a centerlines geometry computed for it. The slices are written to a text file that can be user to represent SimVascular 
segmentation data like that found in a .ctgr file.

The script uses the SimVascular Python API to read in the surface and compute centerlines.

The input surface is assumed 
  1) Closed 
  2) Represents a single branch

The centerline points are sampled using a sampling distance value set by the user.
This is used to select points that are separated by this distace. 
 
Centerline normals can optionally be averaged over the sampling distance to provide 
perhaps a smoother representation of the slice orientation wrt to the surface.

The create_surface_segmentations.py script uses interactive graphics to display geometry for surfaces, centerlines, etc. 
All operations (e.g. extracting centerlines) are initiated using keyboard keys 

    c - Compute centerlines
    e - Extract surface slices along centerlines and write slice geometry to a file
    q - Quit
    s - Select a centerline source point
    t - Select a centerline target point

The order of operations is

   1) Select centerline source points (usually a single point)

   2) Select centerline target points

   3) Compute centerlines

   4) Extract surface slices 

Steps 1-3 can be skipped if centerline geometry is read in from a file.

Centerline geometry is written to a .vtp files with the NAME of the input surface file prefixed.

   NAME-centerlines.vtp - Centerlines 

Slice geometry is written to a .txt file with the NAME of the input surface file prefixed.

   NAME-slices.txt - Centerlines 

The NAME-slices.txt file contains the point coordinates for each slice stored as 
SimVascular segmentation .ctgr file <contour_points> section
```
   <contour_points>
   <point id="0" x="{x-coord-0"    y="{y-coord-0}"  z="{z-coord-0}" /> 
   <point id="1" x="{x-coord-1"    y="{y-coord-1}"  z="{z-coord-1}" /> 
   ...
   <point id="N" x="{x-coord-N"    y="{y-coord-N}"  z="{z-coord-N}" /> 
   </contour_points>
```

Example:
```
   <contour_points>
   <point id="0" x="-28.691776275634766"    y="-56.26897430419922"  z="-151.2576904296875" /> 
   <point id="1" x="-28.481586456298828"    y="-56.267723083496094"  z="-151.2626190185547" /> 
   <point id="2" x="-28.35091781616211"    y="-56.267799377441406"  z="-151.2657012939453" /> 
   ...
   <point id="562" x="-34.31920623779297"    y="-76.07221984863281"  z="-151.87835693359375" />
   </contour_points>
```

The create_surface_segmentations.py script accepts several argumnents 
```
--average-normals (optional) 

   Average normals along sampling distance.

--centerline-file (optional)

   The name of a centerlines .vtp file.

--sample-distance

   The distance used to sample points along a centerline.

--surface-file (required) 

   The name of the input surface (.vtp or .stl) file.
```

Example:

    simvascluar --python -- create_surface_segmentations.py --surface-file=surface.vtp  --sample-distance=9.0 --average-normals

