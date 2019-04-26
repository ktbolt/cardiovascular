
src = p1.cpp 
obj = $(src:.cpp=.o) 

CC = g++

inc = 
copt = -g
copt = -O
PY_CFLAGS  := $(shell python3-config --cflags)
PY_LDFLAGS := $(shell python3-config --ldflags)
#PY_CFLAGS  := $(shell python-config --cflags)
#PY_LDFLAGS := $(shell python-config --ldflags)

# PY_CFLAGS  := -I/Users/parkerda/software/ktbolt/SimVascular/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5/include/python3.5m 
#PY_LDFLAGS := -L/Users/parkerda/software/ktbolt/SimVascular/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5/lib -lpython3.5m

flags =  $(PY_CFLAGS) -std=c++11 -stdlib=libc++ -w $(inc) $(copt)

libs =  $(PY_LDFLAGS) -lm 

p1: p1.o 
	$(CC) -o $@ $? $(libs)

.cpp.o: 
	$(CC) $(flags) -c $<

clean:
	rm -f *.o;

