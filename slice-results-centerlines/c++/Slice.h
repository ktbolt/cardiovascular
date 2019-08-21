
// The Slice class is used to store information about a 2D slice extracted from a
// surface or volume mesh.

#include <iostream>
#include <string>
#include <vector>
#include <iostream>

#include "Graphics.h"
#include "Mesh.h"

#include <vtkActor.h>

#ifndef SLICE_H 
#define SLICE_H 

class Slice {

  public:
    Slice(const int index, const int cellID, const std::string dataName, double pos[3]);
    double area;
    std::string m_DataName;
    double m_CenterlinePosition[3];

    vtkSmartPointer<vtkActor> meshActor;
    vtkSmartPointer<vtkActor> pointActor;
    vtkSmartPointer<vtkActor> sphereActor;
    void AddScalarData(double value);
    void AddVectorData(double values[3]);
    void AddPoint(double point[3]);
    void Write(ofstream& file);

  private:
    int m_CellID; 
    int m_CenterlineIndex; 
    vtkSmartPointer<vtkPolyData> m_Polydata;
    std::vector<double> m_InterpolatedScalarData;
    std::vector<std::array<double,3>> m_InterpolatedVectorData;
    std::vector<std::array<double,3>> m_InterpolationPoints;
};

#endif

