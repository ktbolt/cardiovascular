
#include <iostream>
#include <string>
#include <vector>

#include "Graphics.h"
#include "Mesh.h"

#include <vtkSmartPointer.h>
#include <vtkPolyData.h>

#ifndef CENTERLINES_H 
#define CENTERLINES_H 

class Centerlines {

  public:
    Centerlines();
    void AddGeometry(Graphics& graphics);
    void ReadCenterlines(const std::string fileName);
    void SetMesh(Mesh* mesh); 
    void ShowData(); 
    void create_cell_locator();
    void locate_cell(double point[3], int& index, int& cellId, double& radius, double normal[3], double tangent[3]);
    void write_centerline();

    vtkSmartPointer<vtkPolyData> m_Polydata;
    vtkSmartPointer<vtkDoubleArray> m_NormalData;
    vtkSmartPointer<vtkPointSet> m_PointSet;

  private:
    vtkIdType m_NumLineVerts;
    vtkIdType m_NumLines;
    Mesh* m_Mesh;
    int m_MaterialID;
    vtkIdType m_NumCenterLineVerts;
    std::string m_FileName;
    std::vector<int> m_CenterLineMaterialIDs;
    vtkSmartPointer<vtkPolyData> m_Surface;
    vtkSmartPointer<vtkCellLocator> m_CellLocator;
    vtkSmartPointer<vtkDoubleArray> m_RadiusData;
    vtkSmartPointer<vtkDoubleArray> m_AbscissaData;

};

#endif

