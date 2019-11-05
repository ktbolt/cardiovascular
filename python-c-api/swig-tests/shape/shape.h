
#ifndef SHAPE
#define SHAPE

#include <vector>

class Shape {

  public:
    static int nshapes;
    Shape() { nshapes++; }
    virtual ~Shape() { nshapes--; };
    void Move(double dx, double dy);
    virtual double Area() = 0;
    virtual double Perimeter() = 0;
    virtual std::vector<double> GetList() = 0;
    double  x, y;   

};

#endif

