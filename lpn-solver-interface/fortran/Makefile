
f_src=main.f
f_obj=$(f_src:.f=.o)

$(info f_src: ${f_src})
$(info f_obj: ${f_obj})

c_src=lpn_interface.cpp ../c++/LPNSolverInterface.cpp
c_obj=$(c_src:.cpp=.o)

FC=gfortran
CC = g++

copt = -g
copt = -O
c_flags =  -std=c++11 -I../c++
libs = -lc -lstdc++ -lc++

p: $(f_obj) $(c_obj)
	$(FC) -o $@ $(f_obj) $(c_obj) $(libs)

.f.o: 
	$(FC) $(f_flags) -c $<

.cpp.o: 
	$(CC) $(c_flags) -c $<

clean:
	rm -f *.o p

