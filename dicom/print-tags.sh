
from pathlib import Path
import sys
home = str(Path.home())

## Print the DICOM tags for all files.

dir=home+"/SimVascular/erica-schwarz/data/8"
sn=1.2.840.113619.2.312.3596.12002390.11470.1592004653

for filename in ${dir}/*.dcm; do
  IN=$filename
  arrIN=(${IN//./ })
  n=${arrIN[10]}
  echo "$filename ---> ${n}.txt"
  python3 print-tags.py $filename >  $n.txt
done


