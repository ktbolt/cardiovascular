
src=LPNSolverInterface.cpp main.cpp
obj=$(src:.cpp=.o)

CC = g++

copt = -g
copt = -O
flags =  -std=c++11 -stdlib=libc++ -w $(inc) $(copt)

p: $(obj) LPNSolverInterface.h
	$(CC) -o $@ $(obj) $(libs)

.cpp.o: 
	$(CC) $(flags) -c $<

clean:
	rm -f *.o p

