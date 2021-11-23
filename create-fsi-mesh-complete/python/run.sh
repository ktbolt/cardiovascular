

# Test for no region IDs.
mesh=cylinder
model=cylinder.mdl

mesh=Coronary
model=Coronary.mdl

mesh=aortofemoral
model=aortofemoral.mdl

mesh=demo-bl
model=demo.mdl

mesh=cylinder-bl
model=cylinder.mdl

create-fsi-mesh-complete.py  \
  --volume-mesh=${mesh}.vtu    \
  --surface-mesh=${mesh}.vtp   \
  --fluid-region-id=1          \
  --solid-region-id=2          \
  --mdl-file=${model} 

#print-vtk.py solid-mesh.vtu > solid-mesh.vtu.out
#print-vtk.py solid-outlet.vtp > solid-outlet.vtp.out

