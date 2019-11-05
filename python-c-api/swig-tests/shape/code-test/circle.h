
#include "shape.h"

class Circle : public Shape 
{
  public:
    Circle(double r) : radius(r) { };
    virtual double Area();
    virtual double Perimeter();
    virtual std::vector<double> GetList();
  private:
    double radius;

};

