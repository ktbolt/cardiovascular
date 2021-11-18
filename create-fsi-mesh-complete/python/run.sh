
mesh=demo-bl
model=demo.mdl

mesh=aortofemoral
model=aortofemoral.mdl

# Test for no region IDs.
mesh=cylinder
model=cylinder.mdl

mesh=Coronary
model=Coronary.mdl

mesh=cylinder-bl
model=cylinder.mdl

create-fsi-mesh-complete.py  \
  --volume-mesh=${mesh}.vtu    \
  --surface-mesh=${mesh}.vtp   \
  --fluid-region-id=1          \
  --solid-region-id=2          \
  --mdl-file=${model} 

./print-vtk.py solid-mesh.vtu > solid-mesh-vtu.out
./print-vtk.py solid-inflow.vtp > solid-inflow-vtp.out
./print-vtk.py solid-wall-inner.vtp > solid-wall-inner-vtp.out

./print-vtk.py fluid-wall.vtp > fluid-wall-vtp.out

