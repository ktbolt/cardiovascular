
#include <iostream>
#include <string>
#include <vector>
#include <array>

#include "Graphics.h"
#include "Mesh.h"

#include <vtkSmartPointer.h>
#include <vtkUnstructuredGrid.h>

#ifndef VOLUME_MESH_H 
#define VOLUME_MESH_H 

class VolumeMesh : public Mesh {

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
    vtkSmartPointer<vtkUnstructuredGrid> m_Mesh;
    vtkSmartPointer<vtkPolyData> m_Polydata;
    vtkIdType m_NumPoints;
    vtkIdType m_NumCells;

};

#endif

