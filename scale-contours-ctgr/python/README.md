
This program is used to scale contour data created by SimVascular and stored in .ctgr files. The scaled .ctgr 
is written to a new file.

Usage: scale-contours.py [-h] [--contour-file CONTOUR_FILE]
                         [--surface-file SURFACE_FILE] [--scale SCALE]
                         [--contour-ids CONTOUR_IDS]

  The scaled contours are written to a file named CONTOUR_FILE-scaled.ctgr.
```
Arguments:
  --contour-file CONTOUR_FILE - Input contour (.ctr) file.
  --surface-file SURFACE_FILE - Input surface (.vtp) file.
  --scale SCALE - Contour scale.
  --contour-ids CONTOUR_IDS - Contour IDs (optional).
```
Example:

    python scale-contours.py --surface-file demo.vtp --contour-file aorta.ctgr --scale 0.5  --contour-ids=1,5,10

    Creates aorta-scaled.ctgr.

