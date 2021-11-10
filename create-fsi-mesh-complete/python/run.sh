

mesh=demo-bl
model=demo.mdl

mesh=aortofemoral
model=aortofemoral.mdl

mesh=cylinder
model=cylinder.mdl

mesh=cylinder-bl
model=cylinder.mdl

./create-fsi-mesh-complete.py  \
  --volume-mesh=${mesh}.vtu    \
  --surface-mesh=${mesh}.vtp   \
  --fluid-region-id=1          \
  --solid-region-id=2          \
  --mdl-file=${model} 


