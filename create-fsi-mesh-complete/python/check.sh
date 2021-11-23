
dir=./

model=aortofemoral
model=demo
model=cylinder-bl

if [ $model == "aortofemoral" ]; then
  file1=solid-mesh.vtu 
  file2=solid-Aorta_Smoothed.vtp 

elif [ $model == "demo" ]; then
  file1=solid-mesh.vtu 
  file2=solid-aorta_inlet.vtp 

elif [ $model == "cylinder-bl" ]; then
  file1=solid-mesh.vtu 
  #file2=solid-wall-inner.vtp
  #file2=solid-wall-outer.vtp
  file2=solid-outlet.vtp 

fi

check-mesh.py ${dir}/${file1} ${dir}/${file2}

