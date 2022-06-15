import numpy as np

# This python script will produce a cort.dat file from two input files:
# 1. Plv.dat - This contains the time history of the left ventricle pressure
#              that is used the model the intramyocardial pressure that
#              forces the coronary waveforms out of phase
# 2. cor_params.dat - This file contains the values of the resistances and
#                     capacitances for each coronary outlet in the model

pConv = 1333

n_lcor = 6
pim_scale_lcor = 1.5
pim_scale_rcor = 0.5

# First, load in the left ventricular pressure file
plv_file = open('plv.dat', 'r')

Plv = []

for line in plv_file:
  line_split = line.split()
  Plv.append(line_split)

plv_file.close()

n_plv = len(Plv)

# Read in the coronary parameters file

cor_params = open('cor_params.dat', 'r')
headerline = cor_params.readline()
Ra = []
Ca = []
Ra_micro = []
Cim = []
Rv = []

for line in cor_params:
  line_split = line.split(',')
  Ra.append(float(line_split[1]))
  Ca.append(float(line_split[2]))
  Ra_micro.append(float(line_split[3]))
  Cim.append(float(line_split[4]))
  Rv.append(float(line_split[5]))

cor_params.close()

# Write out the data to cort.dat

cort = open('cort.dat','w')

# Write out the number of timepoints for Plv
cort.write(str(n_plv) + '\n')

count = 0
for i in xrange(0, len(Ra)):
  # Again, write out the number of timepoints for Plv for THIS outlet
  cort.write(str(n_plv) + '\n')
  
  # Calculate the write out the 9 parameters for each outlet
  q0 = Ra[i] + Ra_micro[i] + Rv[i]
  q1 = Ra[i]*Ca[i]*(Ra_micro[i] + Rv[i]) + Cim[i]*(Ra[i] + Ra_micro[i])*Rv[i]
  q2 = Ca[i]*Cim[i]*Ra[i]*Ra_micro[i]*Rv[i]
  p0 = 1.0
  p1 = Ra_micro[i]*Ca[i] + Rv[i]*(Ca[i] + Cim[i])
  p2 = Ca[i]*Cim[i]*Ra_micro[i]*Rv[i]
  b0 = 0.0
  b1 = Cim[i]*Rv[i]
  b2 = 0.0
  
  cort.write(str(q0) + '\n')
  cort.write(str(q1) + '\n')
  cort.write(str(q2) + '\n')
  cort.write(str(p0) + '\n')
  cort.write(str(p1) + '\n')
  cort.write(str(p2) + '\n')
  cort.write(str(b0) + '\n')
  cort.write(str(b1) + '\n')
  cort.write(str(b2) + '\n')
  
  # Write out the mysterious dQinidT and dPinidT parameters
  cort.write('0.0\n')
  cort.write('100.0\n')
  
  Plv_factor = pim_scale_lcor
  if(count >= n_lcor):
    Plv_factor = pim_scale_rcor
  
  # Now write out the intramyocardial pressures
  for j in xrange(0, n_plv):
    cort.write(Plv[j][0] + ' ' + str(Plv_factor*float(Plv[j][1])) + '\n')
    
  count = count + 1

cort.close()





























