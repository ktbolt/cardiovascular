
This program is used to scale contour data created by SimVascular and stored in .ctgr files. 

usage: scale-contours.py [-h] [--contour-file CONTOUR_FILE]
                         [--surface-file SURFACE_FILE] [--scale SCALE]
                         [--contour-ids CONTOUR_IDS]

optional arguments:
  -h, --help            show this help message and exit
  --contour-file CONTOUR_FILE
                        Input contour (.ctr) file.
  --surface-file SURFACE_FILE
                        Input surface (.vtp) file.
  --scale SCALE         Contour scale.
  --contour-ids CONTOUR_IDS
                        Contour IDs (optional).


Example:

    python scale-contours.py --surface-file demo.vtp --contour-file aorta.ctgr --scale 0.5  --contour-ids=1,5,10

