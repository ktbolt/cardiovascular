
#include "circle.h"
#include <cmath>

double Circle::Area()
{
  return M_PI * radius * radius;
}

double 
Circle::Perimeter()
{
}

std::vector<double> 
Circle::GetList()
{ 
  std::vector<double> list{ 1.0, 1.0 };
  return list;
}


