
#include <iostream>
#include <string>
#include "Slice.h"
#include "Mesh.h"

#include <vtkDoubleArray.h>
#include <vtkGeometryFilter.h>
#include <vtkXMLUnstructuredGridReader.h>

Mesh::Mesh()
{
  //cell_locator_ = vtkSmartPointer<vtkCellLocator>::New();
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

//------------
// SlicePlane
//------------
// Slice the surface mesh with a plane.
//
/*
void Mesh::slice_plane(int index, double radius, int cellID, std::string dataName, double pos[3], double normal[3]) 
{
  std::cout << "---------- Slice Surface ----------" << std::endl;

  // Slice surface.
  //
  vtkSmartPointer<vtkPlane> plane = vtkSmartPointer<vtkPlane>::New();
  plane->SetOrigin(pos);
  plane->SetNormal(normal[0], normal[1], normal[2]); 

  vtkSmartPointer<vtkCutter> cutter = vtkSmartPointer<vtkCutter>::New();
  cutter->SetInputData(m_Polydata);
  cutter->SetCutFunction(plane);
  cutter->GenerateValues(1, 0.0, 0.0);

  // Show slice.
  //
  auto showSlice = false;

  if (showSlice) { 
    vtkSmartPointer<vtkPolyDataMapper> cutterMapper = vtkSmartPointer<vtkPolyDataMapper>::New();
    cutterMapper->SetInputConnection(cutter->GetOutputPort());
    cutterMapper->ScalarVisibilityOff();
    //
    vtkSmartPointer<vtkActor> cutterActor = vtkSmartPointer<vtkActor>::New();
    cutterActor->GetProperty()->SetColor(1.0, 0.0, 0.0);
    cutterActor->GetProperty()->SetLineWidth(2);
    cutterActor->SetMapper(cutterMapper);
    m_Graphics->AddGeometry(cutterActor);
  }

  // Get a single Polydata lines geometry from the slice.
  auto lines = GetSliceLines(cutter, pos);

  // Create a Slice object to store slice data.
  auto slice = new Slice(index, cellID, dataName, pos);
  m_Slices.push_back(slice);

  // Calculate the area of the slice.
  SliceArea(radius, lines, slice);

  // Interpolate the surface data to the slice points.
  Interpolate(dataName, lines, slice);
}
*/

