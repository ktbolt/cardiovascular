
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
    void compute_plane_dist(double position[3], double normal[3]);
    void extract_all_slices(vtkPolyData* centerlines);
    void extract_slice(double pos[3], double inscribedRadius, double normal[3]);
    vtkPolyData* find_best_slice(double position[3], vtkPolyData* isosurface);
    void interpolate(vtkPolyData* isosurface);
    void read_mesh(const std::string& fileName);
    void set_graphics(Graphics* graphics);

    Graphics* graphics_;
    std::string mesh_file_name_;
    vtkPolyData* mesh_polydata_;
    vtkDoubleArray* plane_dist_;
    vtkDoubleArray* pressure_data_;
    vtkUnstructuredGrid* unstructured_mesh_;

    vtkSmartPointer<vtkCellLocator> cell_locator_;
};

#endif


