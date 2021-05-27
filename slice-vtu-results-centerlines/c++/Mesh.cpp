
#include "Slice.h"
#include "Mesh.h"

#include <vtkCleanPolyData.h>
#include <vtkContourGrid.h>
#include <vtkDoubleArray.h>
#include <vtkGeometryFilter.h>
#include <vtkGenericCell.h>
#include <vtkPolyDataConnectivityFilter.h>
#include <vtkXMLUnstructuredGridReader.h>

#include <iostream>
#include <string>
#include <chrono>

Mesh::Mesh()
{
}

Mesh::~Mesh()
{
}

//-----------
// read_mesh
//-----------
//
void Mesh::read_mesh(const std::string& file_name)
{
  mesh_file_name_ = file_name;
  std::cout << "[read_mesh] Read mesh: " << file_name << std::endl;
  unstructured_mesh_ = vtkUnstructuredGrid::New();

  auto reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
  reader->SetFileName(file_name.c_str());
  reader->Update();
  unstructured_mesh_->DeepCopy(reader->GetOutput());
  std::cout << "[read_mesh] Number of elements: " << unstructured_mesh_->GetNumberOfCells() << std::endl;

  cell_locator_ = vtkSmartPointer<vtkCellLocator>::New();
  cell_locator_->SetDataSet(unstructured_mesh_);
  cell_locator_->BuildLocator();

  // Get some nodal data.
  pressure_data_ = vtkDoubleArray::SafeDownCast(unstructured_mesh_->GetPointData()->GetArray("pressure"));

  auto geometry_filter = vtkSmartPointer<vtkGeometryFilter>::New();
  geometry_filter->SetInputData(reader->GetOutput());
  geometry_filter->Update();
  mesh_polydata_ = vtkPolyData::New();
  mesh_polydata_->DeepCopy(geometry_filter->GetOutput());

  // Create a cell locator used to interpolate data 
  // at slice points on the surface.
  //m_CellLocator->SetDataSet(m_Polydata);
  //m_CellLocator->BuildLocator();
  std::cout << "[read_mesh] Done. " << std::endl;

  // Add a point data array to store plane distance.
  int num_pts = unstructured_mesh_->GetNumberOfPoints();
  plane_dist_ = vtkDoubleArray::New();
  plane_dist_->SetName("plane_dist");
  plane_dist_->SetNumberOfComponents(1);
  plane_dist_->SetNumberOfTuples(num_pts);
  for (int i = 0; i < num_pts; i++) {
    plane_dist_->SetValue(i,0.0);
  }
  unstructured_mesh_->GetPointData()->AddArray(plane_dist_);
}

//----------------
// get_data_array 
//----------------
//
/*
vtkDoubleArray* Mesh::get_data_array(const std::string& name) 
{
  return vtkDoubleArray::SafeDownCast(unstructured_mesh_->GetPointData()->GetArray(name.c_str()));
}
*/

//--------------
// add_geometry 
//--------------
//
void Mesh::add_geometry()
{
  auto geom = graphics_->create_geometry(mesh_polydata_);
  geom->GetProperty()->SetColor(0.8, 0.0, 0.0);
  //geom->GetProperty()->SetRepresentationToWireframe();
  geom->GetProperty()->EdgeVisibilityOn();
  geom->GetProperty()->SetColor(0.8, 0.8, 0.8);
  geom->GetProperty()->SetOpacity(0.5);
  //geom->GetProperty()->SetRepresentationToWireframe();
  //geom->GetProperty()->FrontfaceCullingOn();
  //geom->GetProperty()->BackfaceCullingOn();
  geom->PickableOff();
  graphics_->add_geometry(geom);
}

void Mesh::set_graphics(Graphics* graphics) 
{ 
  graphics_ = graphics; 
}

//--------------------
// extract_all_slices
//--------------------
//
void Mesh::extract_all_slices(vtkPolyData* centerlines)
{
  std::cout << "[extract_all_slices] " << std::endl;
  std::cout << "[extract_all_slices] ========== Mesh::extract_all_slices ========== " << std::endl;

  auto start_time = std::chrono::steady_clock::now();

  unstructured_mesh_->GetPointData()->SetActiveScalars("plane_dist");

  int num_points = centerlines->GetNumberOfPoints();
  auto points = centerlines->GetPoints();
  auto normal_data = vtkDoubleArray::SafeDownCast(centerlines->GetPointData()->GetArray("CenterlineSectionNormal"));

  for (int i = 0; i < num_points; i++) { 
    double position[3];
    double normal[3];
    points->GetPoint(i, position);
    normal_data->GetTuple(i, normal);

    // Compute the distance of each mesh node to the plane.
    compute_plane_dist(position, normal);

    // Extract the isosurface.
    auto contour = vtkSmartPointer<vtkContourGrid>::New();
    contour->SetInputData(unstructured_mesh_);
    contour->SetValue(0, 0.0);
    contour->ComputeNormalsOff();
    contour->Update();
    auto isosurface = contour->GetOutput();
    //std::cout << "[extract_all_slices] Number of isosurface points: " << isosurface->GetNumberOfPoints() << std::endl;

    // Find the isosurface at the selected point.
    auto best_isosurface = find_best_slice(position, isosurface);

    // Interploate pressure.
    interpolate(best_isosurface);

    /*
    auto geom = graphics_->create_geometry(best_isosurface);
    geom->GetProperty()->SetColor(0.8, 0.0, 0.0);
    geom->PickableOff();
    graphics_->add_geometry(geom);
    */
  }

  auto end_time = std::chrono::steady_clock::now();
  std::chrono::duration<double> elapsed_seconds = end_time - start_time;
  std::cout << "[extract_all_slices] Elapsed time: " << elapsed_seconds.count() << "s\n";
}

//--------------------
// compute_plane_dist 
//--------------------
//
void Mesh::compute_plane_dist(double position[3], double normal[3])
{
  int num_pts = unstructured_mesh_->GetNumberOfPoints();
  double pt[3];
  auto mesh_points = unstructured_mesh_->GetPoints();

  // Compute distance of each mesh point from the slicing plane.
  for (int i = 0; i < num_pts; i++) {
    mesh_points->GetPoint(i, pt);
    mesh_points->GetPoint(i, pt);
    double d = normal[0] * (pt[0] - position[0]) +
               normal[1] * (pt[1] - position[1]) +
               normal[2] * (pt[2] - position[2]);
    plane_dist_->SetValue(i, d);
  }
}

//----------------
// extract_slice
//----------------
//
void Mesh::extract_slice(double position[3], double inscribedRadius, double normal[3])
{
  std::cout << "[extract_slice] " << std::endl;
  std::cout << "[extract_slice] ========== Mesh::extract_slice ========== " << std::endl;
  int num_pts = unstructured_mesh_->GetNumberOfPoints();
  std::cout << "[extract_slice] num_pts: " << num_pts << std::endl;
  double pt[3];
  auto mesh_points = unstructured_mesh_->GetPoints();
  std::cout << "[extract_slice] Normal: " << normal[0] << " " << normal[1] << " " << normal[2] << std::endl;

  // Compute distance of each mesh point from the slicing plane.
  compute_plane_dist(position, normal);

  // Extract isosurface.
  unstructured_mesh_->GetPointData()->SetActiveScalars("plane_dist");
  auto contour = vtkContourGrid::New();
  contour->SetInputData(unstructured_mesh_);
  contour->SetValue(0, 0.0);
  contour->ComputeScalarsOn();
  contour->Update();
  auto isosurface = contour->GetOutput();
  int num_iso_pts = isosurface->GetNumberOfPoints();
  std::cout << "[extract_slice] num_iso_pts: " << num_iso_pts << std::endl;

  // Find the isosurface at the selected point.
  auto best_isosurface = find_best_slice(position, isosurface);

  interpolate(best_isosurface);

  // Show the isosurface.
  auto geom = graphics_->create_geometry(best_isosurface);
  geom->GetProperty()->SetColor(0.8, 0.0, 0.0);
  geom->PickableOff();
  graphics_->add_geometry(geom);
}

//-----------------
// find_best_slice
//-----------------
//
vtkPolyData* 
Mesh::find_best_slice(double position[3], vtkPolyData* isosurface)
{
  auto conn_filter = vtkPolyDataConnectivityFilter::New();
  conn_filter->SetInputData(isosurface);
  conn_filter->SetExtractionModeToSpecifiedRegions();

  double min_d = 1e6;
  int rid = 0;
  double center[3] = {0.0, 0.0, 0.0};
  vtkPolyData* min_comp;

  while (true) { 
    conn_filter->AddSpecifiedRegion(rid);
    conn_filter->Update();
    auto component = vtkPolyData::New();
    component->DeepCopy(conn_filter->GetOutput());
    if (component->GetNumberOfCells() <= 0) { 
      break;
    }
    conn_filter->DeleteSpecifiedRegion(rid);

    auto clean_filter = vtkCleanPolyData::New();
    clean_filter->SetInputData(component);
    clean_filter->Update();
    component = clean_filter->GetOutput();

    auto comp_points = component->GetPoints();
    int num_comp_points = component->GetNumberOfPoints();
    int num_comp_cells = component->GetNumberOfCells();

    double cx = 0.0;
    double cy = 0.0;
    double cz = 0.0;
    for (int i = 0; i < num_comp_points; i++) {
      double pt[3];
      comp_points->GetPoint(i, pt);
      cx += pt[0];
      cy += pt[1];
      cz += pt[2];
    }

    center[0] = cx / num_comp_points;
    center[1] = cy / num_comp_points;
    center[2] = cz / num_comp_points;
    double d = (center[0]-position[0])*(center[0]-position[0]) +
               (center[1]-position[1])*(center[1]-position[1]) +
               (center[2]-position[2])*(center[2]-position[2]);

    if (d < min_d) {
      min_d = d;
      min_comp = component;
    }
    rid += 1;
  }

  return min_comp;
}

//-------------
// interpolate
//-------------
//
void Mesh::interpolate(vtkPolyData* isosurface)
{
 std::cout << "[interpolate] " << std::endl;
  auto points = isosurface->GetPoints();
  double tol2 = 1e-6;
  double localCoords[2];
  double weights[3];
  vtkGenericCell* cell = vtkGenericCell::New();
  auto data = pressure_data_;

  int num_pts = points->GetNumberOfPoints();

  for (vtkIdType i = 0; i < points->GetNumberOfPoints(); i++) {
    double pt[3];
    points->GetPoint(i,pt);
    auto cellID = cell_locator_->FindCell(pt, tol2, cell, localCoords, weights);
    auto numPts = cell->GetNumberOfPoints();
    //auto nodeIDs = vtkIntArray::SafeDownCast(m_Polydata->GetPointData()->GetArray("GlobalNodeID"));
    //auto elemIDs = vtkIntArray::SafeDownCast(m_Polydata->GetCellData()->GetArray("GlobalElementID"));
    //auto elemID = elemIDs->GetValue(cellID);

    std::cout << "[interpolate] CellID: " << cellID << std::endl;
    std::cout << "[interpolate]   localCoords: " << localCoords[0] << "  " << localCoords[1] << "  " << std::endl;
    std::cout << "[interpolate]   weights: " << weights[0] << "  " << weights[1] << "  " << weights[2] << std::endl;
    std::cout << "[interpolate]   Number of cell points: " << numPts << std::endl;

    // Interpolate data at the slice sample points.
    //
    auto numComp = data->GetNumberOfComponents();
    double idata[3] = {0.0, 0.0, 0.0};

    for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
      auto id = cell->PointIds->GetId(pointInd);
      //auto nodeID = nodeIDs->GetValue(id);
      if (numComp == 1) {
        double value = data->GetValue(id);
        idata[0] += weights[pointInd]*value;
        //std::cout << "Value: " << value << std::endl;
        
      } else if (numComp == 3) {
        auto v1 = data->GetComponent(id, 0);
        auto v2 = data->GetComponent(id, 1);
        auto v3 = data->GetComponent(id, 2);
        idata[0] += weights[pointInd]*v1;
        idata[1] += weights[pointInd]*v2;
        idata[2] += weights[pointInd]*v3;
      }
    }

  }

}


