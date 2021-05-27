
#include <iostream>
#include <string>
#include <vector>

#include "Graphics.h"
#include "Mesh.h"

#include <vtkDoubleArray.h>
#include <vtkPolyData.h>
#include <vtkPointSet.h>
#include <vtkSmartPointer.h>

#ifndef CENTERLINES_H 
#define CENTERLINES_H 

class Centerlines {

  public:
    Centerlines();
    ~Centerlines();
    void add_geometry();
    void read_centerlines(const std::string& fileName);
    void set_mesh(Mesh* mesh); 
    //void ShowData(); 
    void create_cell_locator();
    void locate_cell(double point[3], int& index, int& cellId, double& radius, double normal[3]);

    vtkPolyData* polydata_;
    Mesh* mesh_;
    vtkCellLocator* cell_locator_;
    Graphics* graphics_;
    vtkPointSet* point_set_;
    vtkDoubleArray* normal_data_;
    vtkDoubleArray* radius_data_;
};

#endif

