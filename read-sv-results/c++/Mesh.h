
#include <iostream>
#include <string>
#include <vector>

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
    virtual void ReadMesh(const std::string fileName) = 0;
    virtual bool IsSurface() = 0;

  protected:
    std::vector<std::string> m_PointDataNames;

};

#endif


