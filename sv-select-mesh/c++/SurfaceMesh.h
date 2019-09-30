
#include <iostream>
#include <string>
#include <vector>

#include "Graphics.h"
#include "Mesh.h"

#include <vtkSmartPointer.h>
#include <vtkPolyData.h>

#ifndef SURFACE_MESH_H 
#define SURFACE_MESH_H 

class SurfaceMesh : public Mesh {

  public:
    void AddGeometry(Graphics& graphics);
    void FindData();
    void FixMesh();
    vtkSmartPointer<vtkDoubleArray> GetDataArray(std::string name);
    vtkSmartPointer<vtkDataSet> GetMesh();
    vtkSmartPointer<vtkPolyData> GetPolyData();
    bool IsSurface();
    void ReadMesh(const std::string fileName);
    void CheckNodeIDs();

  private:
    vtkSmartPointer<vtkPolyData> m_Polydata;
    vtkIdType m_NumPoints;
    vtkIdType m_NumPolys;

};

#endif

