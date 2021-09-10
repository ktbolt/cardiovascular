
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
    void read_mesh(const std::string& fileName);
    void remove_data_arrays(const std::set<std::string>& slice_data_names);
    vtkPolyData* trim_slice(vtkPolyData* slice, double position[3], double radius); 
    void write_slice(vtkPolyData* slice, int id);

    Graphics* graphics_;

    std::string mesh_file_name_;

    // The name of the scalar field used to slice the mesh.
    const char* slice_scalar_name_;

    vtkDoubleArray* plane_dist_;

    vtkPolyData* mesh_polydata_;

    vtkDoubleArray* pressure_data_;

    bool trim_slice_using_incribed_sphere_;

    vtkUnstructuredGrid* unstructured_mesh_;

    vtkDoubleArray* velocity_data_;
};

#endif


