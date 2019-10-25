
#include "shape.h"

class Square : public Shape {
  public:
    Square(double w) : width(w) { };
    virtual double area();
    virtual double perimeter();
  private:
    double width;
};

