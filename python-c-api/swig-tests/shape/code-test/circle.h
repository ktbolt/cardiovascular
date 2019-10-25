
#include "shape.h"

class Circle : public Shape 
{
  public:
    Circle(double r) : radius(r) { };
    virtual double area();
    virtual double perimeter();

  private:
    double radius;

};

