
set datafile separator ','

set ylabel "Flow"
set xlabel "Time"
set grid 

set key outside

plot for [col=1:4] './output/1dsolver_pressure.csv' using 1:col with lines title columnheader

pause -1
