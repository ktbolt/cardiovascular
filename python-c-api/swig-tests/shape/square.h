
#include "shape.h"

class Square : public Shape {
  public:
    Square(double w) : width(w) { };
    virtual double Area();
    virtual double Perimeter();
    virtual std::vector<double> GetList();
  private:
    double width;
};

