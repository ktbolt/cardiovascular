
#include <iostream>
#include <set>
#include <string>
#include <vector>

#include <vtkDataSet.h>
#include <vtkDoubleArray.h>
#include <vtkSmartPointer.h>
#include <vtkUnstructuredGrid.h>

class Graphics;

#ifndef MESH_H 
#define MESH_H 

class Mesh {
  public:
    Mesh();
    ~Mesh();

    void add_geometry();
    void read_mesh(const std::string& fileName);
    void set_graphics(Graphics* graphics);

    vtkUnstructuredGrid* unstructured_mesh_;
    vtkPolyData* mesh_polydata_;
    std::string mesh_file_name_;
    Graphics* graphics_;
};

#endif


