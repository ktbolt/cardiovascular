
src = main.cpp WriteJson.cpp WriteRcrJson.cpp
objs = $(src:.cpp=.o )

flags=-std=c++11

p: $(objs) 
	g++ -o p $(objs) 

main.o: main.cpp
	g++ $(flags) -c main.cpp

WriteJson.o: WriteJson.cpp WriteJson.h
	g++ $(flags) -c WriteJson.cpp

WriteRcrJson.o: WriteRcrJson.cpp WriteRcrJson.h WriteJson.h
	g++ $(flags) -c WriteRcrJson.cpp

