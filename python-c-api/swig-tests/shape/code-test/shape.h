
#ifndef SHAPE
#define SHAPE

class Shape {

  public:
    static int nshapes;
    Shape() { nshapes++; }
    virtual ~Shape() { nshapes--; };
    void move(double dx, double dy);
    virtual double area() = 0;
    virtual double perimeter() = 0;
    double  x, y;   

};

#endif

