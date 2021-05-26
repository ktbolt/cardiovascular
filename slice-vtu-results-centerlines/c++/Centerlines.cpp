
// version master

#include <iostream>
#include <string>
#include "Centerlines.h"

#include <vtkCellData.h>
#include <vtkCellLocator.h>
#include <vtkPointData.h>
#include <vtkXMLPolyDataReader.h>

//-------------
// Centerlines
//-------------
//
Centerlines::Centerlines()
{
}

Centerlines::~Centerlines()
{
  std::cout << "[~Centerline] **** dtor **** " << std::endl;
}

//------------------
// read_centerlines 
//------------------
//
void Centerlines::read_centerlines(const std::string& file_name)
{
  std::cout << "[read_centerlines] Read centerlines: " << file_name << std::endl;

  auto reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  reader->SetFileName(file_name.c_str());
  reader->Update();

  polydata_ = vtkPolyData::New();
  polydata_->DeepCopy(reader->GetOutput());
  std::cout << "[read_centerlines] Number of points: " << polydata_->GetNumberOfPoints() << std::endl;

  // Create a picking locator.
  create_cell_locator();

  normal_data_ = vtkDoubleArray::SafeDownCast(polydata_->GetPointData()->GetArray("CenterlineSectionNormal"));
  std::cout << "[read_centerlines] normal_data_: " << normal_data_ << std::endl;
  if (normal_data_ == nullptr) { 
    std::cout << "[read_centerlines] WARNING: No CenterlineSectionNormal data. " << std::endl;
  }
  std::cout << "[read_centerlines] Done. " << std::endl;
}

//--------------
// add_geometry 
//--------------
//
void Centerlines::add_geometry()
{
  std::cout << "========== Centerlines::add_geometry ========== " << std::endl;
  std::cout << "[add_geometry] " << std::endl;
  std::cout << "[add_geometry] graphics_ " << graphics_ << std::endl;
  auto geom = graphics_->create_geometry(polydata_);
  geom->GetProperty()->SetColor(0.0, 0.8, 0.0);
  //geom->GetProperty()->SetRepresentationToWireframe();
  //geom->GetProperty()->EdgeVisibilityOn();
  geom->GetProperty()->SetLineWidth(8.0);
  //geom->SetPickable(0);
  graphics_->add_geometry(geom);
  std::cout << "[add_geometry] Done " << std::endl;
}

//----------
// set_mesh
//----------
//
void Centerlines::set_mesh(Mesh* mesh)
{
  mesh_ = mesh;
}

//---------------------
// create_cell_locator
//---------------------
// Create a vtkCellLocator to find picked points in centerlines.
//
void Centerlines::create_cell_locator()
{
  std::cout << "[create_cell_locator] " << std::endl;
  cell_locator_ = vtkCellLocator::New();
  cell_locator_->SetDataSet(polydata_);
  cell_locator_->BuildLocator();
  std::cout << "[create_cell_locator] cell_locator_ " << cell_locator_ << std::endl;

  point_set_ = vtkPolyData::New();
  point_set_->SetPoints(polydata_->GetPoints());
}

//-------------
// locate_cell
//-------------
// Locate the given point in centerlines.
//
void Centerlines::locate_cell(double point[3], int& index, int& cellID, double& radius, double normal[3])
{
  std::cout << "[locate_cell] " << std::endl;
  std::cout << "[locate_cell] Point: " << point[0] << " " << point[1] << " " << point[2] << std::endl;

  //std::cout << "[locate_cell] cell_locator_ " << cell_locator_ << std::endl;

  // Find the point in centerlines that is closest to the selected point.
  // 
  // Note that cellLocator->FindClosestPoint(point, closestPoint, cellId, subId, closestPointDist2) 
  // does not return the index of the selected point in centerlines in the returned variable 'subId'. 
  // In fact, it is not ducumented and no one seems to know what it represents!
  //
  double closestPoint[3];
  double closestPointDist2; 
  vtkIdType cellId; 
  int subId; 
  cell_locator_->FindClosestPoint(point, closestPoint, cellId, subId, closestPointDist2);
  index = point_set_->FindPoint(point);
  std::cout << "[locate_cell] Closest point: " << closestPoint[0] << " " << closestPoint[1] << " " << closestPoint[2] << std::endl;
  std::cout << "[locate_cell] Distance to closest point: " << closestPointDist2 << std::endl;
  std::cout << "[locate_cell] CellId: " << cellId << std::endl;
  std::cout << "[locate_cell] Index: " << index << std::endl;

  index = 0;
  std::cout << "[locate_cell] normal_data_: " << normal_data_ << std::endl;

  if (normal_data_ != nullptr) {
    normal_data_->GetTuple(index, normal);
    std::cout << "[locate_cell] Normal: " << normal[0] << " " << normal[1] << " " << normal[2] << std::endl;
  }

  cellID = cellId;
}

