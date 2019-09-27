
#include <iostream>
#include <set>
#include <string>
#include <vector>
#include <array>

#include <vtkDataSet.h>
#include <vtkDoubleArray.h>
#include <vtkSmartPointer.h>

class Graphics;

#ifndef MESH_H 
#define MESH_H 

class Mesh {
  public:
    virtual void AddGeometry(Graphics& graphics) = 0;
    virtual vtkSmartPointer<vtkDoubleArray> GetDataArray(std::string name) = 0;
    virtual vtkSmartPointer<vtkDataSet> GetMesh() = 0;
    virtual void FindData() = 0;
    virtual void CheckNodeIDs() = 0;
    virtual void ReadMesh(const std::string fileName) = 0;
    virtual bool IsSurface() = 0;
    bool HasData(const std::string& name);
    std::vector<std::array<double,3>> m_DupeCoords;

  protected:
    std::set<std::string> m_PointDataNames;
};

#endif


