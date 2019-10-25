
src = circle.cpp main.cpp shape.cpp square.cpp
obj = $(src:.cpp=.o)
flags=-std=c++11

exe = p

$(exe): $(obj)
	g++ -o $(exe) $(obj) $(libs) 

.cpp.o: 
	g++ $(flags) -c $<


