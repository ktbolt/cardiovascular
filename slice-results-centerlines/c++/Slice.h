
// The Slice class is used to store information about a 2D slice extracted from a
// surface or volume mesh.

#include <iostream>
#include <string>
#include <vector>

#include "Graphics.h"
#include "Mesh.h"

#include <vtkActor.h>

#ifndef SLICE_H 
#define SLICE_H 

class Slice {

  public:
    Slice(const int index, const std::string dataName, double pos[3]);
    double area;
    vtkSmartPointer<vtkActor> meshActor;
    vtkSmartPointer<vtkActor> pointActor;

  private:
    int m_CenterlineIndex; 
    std::string m_DataName;
    double m_CenterlinePosition[3];
    vtkSmartPointer<vtkPolyData> m_Polydata;

};

#endif

