
#include "Slice.h"
#include "Mesh.h"

#include <vtkCleanPolyData.h>
#include <vtkClipPolyData.h>
#include <vtkContourGrid.h>
#include <vtkDoubleArray.h>
#include <vtkExtractGeometry.h>
#include <vtkGeometryFilter.h>
#include <vtkGenericCell.h>
#include <vtkPolyDataConnectivityFilter.h>
#include <vtkSelectEnclosedPoints.h>
#include <vtkSphere.h>
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

  // Remove data arrays we don't want to generate slice data for.
  std::set<std::string> slice_data_names = { "pressure", "velocity" };
  remove_data_arrays(slice_data_names);

  // Get some nodal data.
  pressure_data_ = vtkDoubleArray::SafeDownCast(unstructured_mesh_->GetPointData()->GetArray("pressure"));
  velocity_data_ = vtkDoubleArray::SafeDownCast(unstructured_mesh_->GetPointData()->GetArray("velocity"));

  auto geometry_filter = vtkSmartPointer<vtkGeometryFilter>::New();
  geometry_filter->SetInputData(reader->GetOutput());
  geometry_filter->Update();
  mesh_polydata_ = vtkPolyData::New();
  mesh_polydata_->DeepCopy(geometry_filter->GetOutput());

  // Create a cell locator used to interpolate data 
  // at slice points on the surface.
  cell_locator_ = vtkSmartPointer<vtkCellLocator>::New();
  cell_locator_->SetDataSet(unstructured_mesh_);
  cell_locator_->BuildLocator();

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

  std::cout << "[read_mesh] Done. " << std::endl;
}

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
  auto radius_data = vtkDoubleArray::SafeDownCast(centerlines->GetPointData()->GetArray("MaximumInscribedSphereRadius"));

  for (int i = 0; i < num_points; i++) { 
    double position[3];
    double normal[3];
    points->GetPoint(i, position);
    normal_data->GetTuple(i, normal);
    double radius = radius_data->GetValue(i);

    // Compute the distance of each mesh node to the plane.
    compute_plane_dist(position, normal);

    // Extract the slice.
    auto contour = vtkSmartPointer<vtkContourGrid>::New();
    contour->SetInputData(unstructured_mesh_);
    contour->SetValue(0, 0.0);
    contour->ComputeNormalsOff();
    contour->Update();
    auto slice = contour->GetOutput();

    // Find the isosurface at the selected point.
    // auto best_slice = find_best_slice(position, slice);

    // Trim the slice using the incribed sphere radius.
    auto trimmed_slice = trim_slice(slice, position, radius);
    //auto trimmed_slice = trim_slice(best_slice, position, radius);

    /*
    auto geom = graphics_->create_geometry(trimmed_slice);
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
// remove_data_arrays
//--------------------
//
void Mesh::remove_data_arrays(const std::set<std::string>& slice_data_names)
{
  std::cout << "[remove_data_arrays] " << std::endl;
  std::cout << "[remove_data_arrays] ========== Mesh::remove_data_arrays ========== " << std::endl;

  // Note: Can't remove arrays in this loop because it crashes vtk,
  // changes unstructured_mesh_ data it seems.
  //
  vtkIdType num_point_arrays = unstructured_mesh_->GetPointData()->GetNumberOfArrays();
  std::cout << "[remove_data_arrays] Number of node data arrays: " << num_point_arrays << std::endl;
  std::vector<std::string> remove_data_names;

  for (int i = 0; i < num_point_arrays; i++) {
    int type = unstructured_mesh_->GetPointData()->GetArray(i)->GetDataType();
    auto name = unstructured_mesh_->GetPointData()->GetArrayName(i);
    int num_comp = unstructured_mesh_->GetPointData()->GetNumberOfComponents();
    if (slice_data_names.count(name) == 0) {
      std::cout << "[remove_data_arrays] Remove data array: " << name << std::endl;
      remove_data_names.push_back(std::string(name));
    }
  }

  for (auto const& name : remove_data_names) { 
    unstructured_mesh_->GetPointData()->RemoveArray(name.c_str());
  }
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
  auto slice = contour->GetOutput();
  int num_slice_pts = slice ->GetNumberOfPoints();
  std::cout << "[extract_slice] num_slice_pts: " << num_slice_pts << std::endl;

  // Show the slice.
  /*
  auto slice_geom = graphics_->create_geometry(slice);
  slice_geom->GetProperty()->SetRepresentationToWireframe();
  slice_geom->GetProperty()->SetColor(0.0, 0.5, 0.0);
  slice_geom->GetProperty()->SetLineWidth(1);
  slice_geom->PickableOff();
  graphics_->add_geometry(slice_geom);
  */

  // For multipled disjoint slice geometry find the geometry
  // with center closest to the selected point.
/*
  auto best_slice = find_best_slice(position, slice);

  // Show the best slice.
  auto best_slice_geom = graphics_->create_geometry(best_slice);
  best_slice_geom->GetProperty()->SetRepresentationToWireframe();
  best_slice_geom->GetProperty()->SetColor(1.0, 0.0, 0.0);
  best_slice_geom->GetProperty()->SetLineWidth(4);
  best_slice_geom->PickableOff();
  graphics_->add_geometry(best_slice_geom);
*/

  // Trim the slice using the incribed sphere radius.
  auto trimmed_slice = trim_slice(slice, position, inscribedRadius);
  //auto trimmed_slice = trim_slice(best_slice, position, inscribedRadius);
  std::cout << "[extract_slice] num trim pts: " << trimmed_slice->GetNumberOfPoints() << std::endl;

  // Write the slice to a .vtp file.
  //write_slice(best_slice, 1);

  // Show the trimmed slice.
  auto trim_geom = graphics_->create_geometry(trimmed_slice);
  //trim_geom->GetProperty()->SetRepresentationToWireframe();
  trim_geom->GetProperty()->SetColor(1.0, 0.0, 0.0);
  trim_geom->GetProperty()->EdgeVisibilityOn();
  //trim_geom->GetProperty()->SetLineWidth(1);
  trim_geom->PickableOff();
  graphics_->add_geometry(trim_geom);

}

//------------
// trim_slice
//------------
//
vtkPolyData*
Mesh::trim_slice(vtkPolyData* slice, double position[3], double radius)
{
  auto points = slice->GetPoints();
  int num_points = slice->GetNumberOfPoints();
  int num_cells = slice->GetNumberOfCells();
  double center[3] = {0.0, 0.0, 0.0};
  for (int i = 0; i < num_points; i++) {
    double pt[3];
    points->GetPoint(i, pt);
    center[0] += pt[0];
    center[1] += pt[1];
    center[2] += pt[2];
  }

  center[0] /= num_points;
  center[1] /= num_points;
  center[2] /= num_points;

  // Creae a sphere implicit function.
  auto sphere = vtkSphere::New();
  sphere->SetCenter(position);
  sphere->SetRadius(radius);

  // Extract geometry within the sphere implicit function.
  /*
  auto extract = vtkExtractGeometry::New();
  extract->SetInputData(slice);
  extract->SetImplicitFunction(sphere);
  extract->ExtractInsideOn();
  extract->ExtractBoundaryCellsOn();
  extract->Update();
  auto extract_grid = extract->GetOutput();

  auto geometry_filter = vtkSmartPointer<vtkGeometryFilter>::New();
  geometry_filter->SetInputData(extract_grid);
  geometry_filter->Update();
  trimmed_slice->DeepCopy(geometry_filter->GetOutput());
  */

  // Clip geometry to the sphere implicit function.
  auto clip = vtkClipPolyData::New();
  clip->SetInputData(slice);
  clip->SetClipFunction(sphere);
  clip->InsideOutOn();
  clip->Update();

  auto trimmed_slice = vtkPolyData::New();
  trimmed_slice->DeepCopy(clip->GetOutput());

  return trimmed_slice;
}

//-----------------
// find_best_slice
//-----------------
// For multipled disjoint slice geometry find the geometry
// with center closest to the selected point.
//
vtkPolyData* 
Mesh::find_best_slice(double position[3], vtkPolyData* slice)
{
  auto conn_filter = vtkPolyDataConnectivityFilter::New();
  conn_filter->SetInputData(slice);
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
// Interploate mesh nodal date (e.g. pressure) to the slice geometry.
//
void Mesh::interpolate(vtkPolyData* slice)
{
  double tol2 = 1e-6;

  auto slice_points = slice->GetPoints();
  int num_slice_pts = slice_points->GetNumberOfPoints();
  vtkGenericCell* cell = vtkGenericCell::New();

  auto slice_pressure_data = vtkDoubleArray::New();
  slice_pressure_data->SetName("pressure");
  slice_pressure_data->SetNumberOfComponents(1);
  slice_pressure_data->SetNumberOfTuples(num_slice_pts);
  for (int i = 0; i < num_slice_pts; i++) {
    slice_pressure_data->SetValue(i,0.0);
  }
  //slice->GetPointData()->AddArray(slice_pressure_data);

  auto slice_velocity_data = vtkDoubleArray::New();
  slice_velocity_data->SetName("velocity");
  slice_velocity_data->SetNumberOfComponents(3);
  slice_velocity_data->SetNumberOfTuples(num_slice_pts);
  for (int i = 0; i < num_slice_pts; i++) {
    slice_velocity_data->SetComponent(i, 0, 0.0);
    slice_velocity_data->SetComponent(i, 1, 0.0);
    slice_velocity_data->SetComponent(i, 2, 0.0);
  }
  //slice->GetPointData()->AddArray(slice_velocity_data);


  for (int i = 0; i < num_slice_pts; i++) {
    double pt[3];
    slice_points->GetPoint(i,pt);

    double localCoords[2];
    double weights[3];
    auto cellID = cell_locator_->FindCell(pt, tol2, cell, localCoords, weights);
    auto numPts = cell->GetNumberOfPoints();
    //auto nodeIDs = vtkIntArray::SafeDownCast(m_Polydata->GetPointData()->GetArray("GlobalNodeID"));
    //auto elemIDs = vtkIntArray::SafeDownCast(m_Polydata->GetCellData()->GetArray("GlobalElementID"));
    //auto elemID = elemIDs->GetValue(cellID);

    //std::cout << "[interpolate] CellID: " << cellID << std::endl;
    //std::cout << "[interpolate]   localCoords: " << localCoords[0] << "  " << localCoords[1] << "  " << std::endl;
    //std::cout << "[interpolate]   weights: " << weights[0] << "  " << weights[1] << "  " << weights[2] << std::endl;
    //std::cout << "[interpolate]   Number of cell points: " << numPts << std::endl;

    // Interpolate data at the slice points.
    //
    double pressure_sum = 0.0;
    double velocity_sum[3] = {0.0, 0.0, 0.0};

    for (int j = 0; j < numPts; j++) {
      auto id = cell->PointIds->GetId(j);

      double value = pressure_data_->GetValue(id);
      pressure_sum += weights[j]*value;
        
      auto v1 = velocity_data_->GetComponent(id, 0);
      auto v2 = velocity_data_->GetComponent(id, 1);
      auto v3 = velocity_data_->GetComponent(id, 2);
      velocity_sum[0] += weights[j]*v1;
      velocity_sum[1] += weights[j]*v2;
      velocity_sum[2] += weights[j]*v3;
    }

    slice_pressure_data->SetValue(i, pressure_sum);

    slice_velocity_data->SetComponent(i, 0, velocity_sum[0]);
    slice_velocity_data->SetComponent(i, 1, velocity_sum[1]);
    slice_velocity_data->SetComponent(i, 2, velocity_sum[2]);
  }

}

//-------------
// write_slice
//-------------
//
void Mesh::write_slice(vtkPolyData* slice, int id)
{
  std::stringstream file_name;
  file_name << "slice-" << id << ".vtp";
  vtkSmartPointer<vtkXMLPolyDataWriter> writer = vtkSmartPointer<vtkXMLPolyDataWriter>::New();
  writer->SetFileName(file_name.str().c_str());
  writer->SetInputData(slice);
  writer->Update();
  writer->Write();
}
