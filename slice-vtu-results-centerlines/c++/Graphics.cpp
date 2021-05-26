
#include "Graphics.h" 

#include <vtkCellData.h>
#include <vtkCellPicker.h>
//
#include <vtkExtractSelectedPolyDataIds.h>
#include <vtkExtractSelection.h>
//
#include <vtkGenericCell.h>
//
#include <vtkNamedColors.h>
#include <vtkPointData.h>
//
#include <vtkSelection.h>
#include <vtkSelectionNode.h>
//
#include <vtkUnstructuredGrid.h>

//----------
// Graphics
//----------
//
Graphics::Graphics()
{
  mesh_ = nullptr;
  centerlines_ = nullptr;

  // Add a renderer.
  renderer_ = vtkSmartPointer<vtkRenderer>::New();
  renderer_->SetBackground(1.0, 1.0, 1.0);

  // Add a render window.
  render_window_ = vtkSmartPointer<vtkRenderWindow>::New();
  render_window_->AddRenderer(renderer_);
  render_window_->SetSize(1000, 1000);
  render_window_->Render();
  render_window_->SetWindowName("Simulation Results Surface Slicer");

  // Add window interactor to use trackball and intercept key presses.
  //
  render_window_interactor_ = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  render_window_interactor_->SetRenderWindow(render_window_);

  interaction_style_ = vtkSmartPointer<MouseCenterlineInteractorStyle>::New();
  //interaction_style_ = vtkSmartPointer<MouseMeshInteractorStyle>::New();

  interaction_style_->set_graphics(this);
  render_window_interactor_->SetInteractorStyle(interaction_style_);
  interaction_style_->SetDefaultRenderer(renderer_);
  render_window_interactor_->SetInteractorStyle(interaction_style_);
}

Mesh* Graphics::get_mesh()
{
  return mesh_;
}
void Graphics::set_mesh(Mesh* mesh)
{
  mesh_ = mesh;
}

void Graphics::set_centerlines(Centerlines* centerlines)
{
  centerlines_ = centerlines;
  interaction_style_->set_centerlines(centerlines);
}

void Graphics::start()
{
  //render_window_interactor->Initialize();
  render_window_interactor_->Start();
}

//----------------
// CreateGeometry 
//----------------
//
vtkActor* Graphics::create_geometry(vtkPolyData* polyData)
{
  auto mapper = vtkDataSetMapper::New();
  mapper->SetInputData(polyData);
  mapper->ScalarVisibilityOff();
  auto actor = vtkActor::New();
  actor->SetMapper(mapper);
  return actor; 
}

//-------------
// AddGeometry
//-------------
//
void Graphics::add_geometry(vtkActor* geom)
{
  renderer_->AddActor(geom);
}

std::string Graphics::get_data_name() 
{
  return data_name_;
}

void Graphics::set_data_name(const std::string& name) 
{
/*
  if (mesh_ != nullptr) {
    if (mesh_->HasData(name)) {
      data_name_ = name;
    } else {
      std::cout << "WARNING: The mesh does not have data named '" << name << "'" << std::endl;
    }
  } else {
      std::cout << "WARNING: The mesh is not set for graphics." << "'" << std::endl;
  }
*/
}

// Create a circle
vtkActor* Graphics::create_circle()
{
  vtkSmartPointer<vtkRegularPolygonSource> polygonSource = vtkSmartPointer<vtkRegularPolygonSource>::New();
  polygonSource->SetNumberOfSides(50);
  polygonSource->SetRadius(5);
  polygonSource->SetCenter(0, 0, 0);

  vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  mapper->SetInputConnection(polygonSource->GetOutputPort());;
      
  auto actor = vtkActor::New();
  actor->SetMapper(mapper);
  return actor;
}   

void Graphics::refresh()
{
  render_window_->Render();
}

/////////////////////////////////////////////////////////////////////////
//            M o u s e M e s h I n t e r a c t o r S t y l e          //
/////////////////////////////////////////////////////////////////////////

// This class defines a mouse interactor used to select a surface
// element (triangle) and display its nodal data.

MouseMeshInteractorStyle::MouseMeshInteractorStyle()
{
  selected_mapper_ = vtkSmartPointer<vtkDataSetMapper>::New();
  selected_actor_ = vtkSmartPointer<vtkActor>::New();
  colors_ = vtkSmartPointer<vtkNamedColors>::New();
}

void MouseMeshInteractorStyle::set_graphics(Graphics* graphics)
{
  graphics_ = graphics;
}

// Process a keyboard press event.
//
void MouseMeshInteractorStyle::OnKeyPress() 
{
  // Get the keypress.
  vtkRenderWindowInteractor *rwi = this->Interactor;
  std::string key = rwi->GetKeySym();
  std::cout << "Pressed key: " << key << std::endl;

  if ((key == "Escape") || (key == "q")) {
    exit(0);
  }
  else if (key == "s") {
    select_cell();
  }

  // Forward events
  //vtkInteractorStyleTrackballCamera::OnLeftButtonDown();

}

//-------------
// select_cell 
//-------------
//
void MouseMeshInteractorStyle::select_cell() 
{
  std::cout << "[select_cell] " << std::endl;
  vtkSmartPointer<vtkNamedColors> colors = vtkSmartPointer<vtkNamedColors>::New();

  // Get the location of the click (in window coordinates)
  int* pos = this->GetInteractor()->GetEventPosition();

  vtkSmartPointer<vtkCellPicker> picker = vtkSmartPointer<vtkCellPicker>::New();
  picker->SetTolerance(0.1);

  // Pick from this location.
  picker->Pick(pos[0], pos[1], 0, this->GetDefaultRenderer());

  double* worldPosition = picker->GetPickPosition();
  auto cellID = picker->GetCellId();

  if (cellID == -1) {
    return;
  }

  std::cout << "Pick position is: " << worldPosition[0] << " " << worldPosition[1] << " " << worldPosition[2] << endl;
  select_mesh(cellID);
}

//-------------
// SelectMesh 
//-------------
//
void MouseMeshInteractorStyle::select_mesh(int cellID)
{ 
  std::cout << "[select_mesh] " << std::endl;
  vtkSmartPointer<vtkIdTypeArray> ids = vtkSmartPointer<vtkIdTypeArray>::New();
  ids->SetNumberOfComponents(1);
  ids->InsertNextValue(cellID);

  vtkSmartPointer<vtkSelectionNode> selectionNode = vtkSmartPointer<vtkSelectionNode>::New();
  selectionNode->SetFieldType(vtkSelectionNode::CELL);
  selectionNode->SetContentType(vtkSelectionNode::INDICES);
  selectionNode->SetSelectionList(ids);

  vtkSmartPointer<vtkSelection> selection = vtkSmartPointer<vtkSelection>::New();
  selection->AddNode(selectionNode);

  //if (graphics_->get_mesh()->IsSurface()) {
    //select_mesh(cellID, selection);
  //}

}

//-------------------
// SelectSurfaceMesh
//-------------------
//
/*
void MouseMeshInteractorStyle::select_mesh(int cellID, vtkSmartPointer<vtkSelection> selection)
{ 
  auto mesh = graphics_->GetMesh();
  vtkPolyData* polydata = vtkPolyData::SafeDownCast(mesh->GetMesh());
  auto dataName = graphics_->get_data_name();
  auto data = mesh->GetDataArray(dataName);

  // Extract a list of cells from polydata.
  //
  vtkSmartPointer<vtkExtractSelection> extractSelection = vtkSmartPointer<vtkExtractSelection>::New();
  //vtkSmartPointer<vtkExtractSelectedPolyDataIds> extractSelection = vtkSmartPointer<vtkExtractSelectedPolyDataIds>::New();
  extractSelection->SetInputData(0, polydata); 
  extractSelection->SetInputData(1, selection);
  extractSelection->Update();

  // Get selected cells as a vtkPolyData.
  //
  vtkSmartPointer<vtkUnstructuredGrid> selected = vtkSmartPointer<vtkUnstructuredGrid>::New();
  //vtkSmartPointer<vtkPolyData> selected = vtkSmartPointer<vtkPolyData>::New();
  selected->ShallowCopy(extractSelection->GetOutput());
  std::cout << "There are " << selected->GetNumberOfPoints() << " points in the selection." << std::endl;
  std::cout << "There are " << selected->GetNumberOfCells() << " cells in the selection." << std::endl;

   // Print cell ID and connectivity.
   //
   vtkGenericCell* cell = vtkGenericCell::New();
   polydata->GetCell(cellID, cell);
   auto numPts = cell->GetNumberOfPoints();
   auto nodeIDs = vtkIntArray::SafeDownCast(polydata->GetPointData()->GetArray("GlobalNodeID"));
   auto elemIDs = vtkIntArray::SafeDownCast(polydata->GetCellData()->GetArray("GlobalElementID"));
   auto elemID = elemIDs->GetValue(cellID);
   std::cout << "Cell ID is: " << cellID << std::endl;
   std::cout << "  Elem ID: " << elemID << std::endl;
   std::cout << "  Number of cell points: " << numPts << std::endl;
   std::cout << "  Connectivity: ";
   for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
     auto id = cell->PointIds->GetId(pointInd);
     auto nodeID = nodeIDs->GetValue(id);
     std::cout << nodeID << " ";
   }
   std::cout << std::endl;

   // Print cell data.
   if (dataName != "") {
     std::cout << std::endl;
     std::cout << "Cell Data: " << std::endl;
     std::cout << "  Name: " << dataName << std::endl;
     auto numComp = data->GetNumberOfComponents();

     for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
       auto id = cell->PointIds->GetId(pointInd);
       auto nodeID = nodeIDs->GetValue(id);
       if (numComp == 1) { 
         double value = data->GetValue(id);
         std::cout << "  ID: " << nodeID << "   Value: " << value << std::endl;
       } else if (numComp == 3) { 
         auto v1 = data->GetComponent(id, 0);
         auto v2 = data->GetComponent(id, 1);
         auto v3 = data->GetComponent(id, 2);
         std::cout << "  Node ID: " << nodeID << "   Values: " << v1 << " " << v2 << " " << v3 << std::endl;
       }
     }
   }

  // Display the selected cell.
  //
  selected_mapper_->SetInputData(selected);
  selected_mapper_->ScalarVisibilityOff();
  selected_actor_->SetMapper(selected_mapper_);
  //selectedActor->GetProperty()->EdgeVisibilityOn();
  //selected_actor_->GetProperty()->SetRepresentationToWireframe();
  selected_actor_->GetProperty()->SetColor(colors_->GetColor3d("Green").GetData());
  selected_actor_->GetProperty()->SetLineWidth(4);

  this->Interactor->GetRenderWindow()->GetRenderers()->GetFirstRenderer()->AddActor(selected_actor_);
  this->Interactor->GetRenderWindow()->Render();
}
*/

//void MouseInteractorStyle::OnLeftButtonDown()
//{
//}

vtkStandardNewMacro(MouseMeshInteractorStyle);

/////////////////////////////////////////////////////////////////////////////////////
//            M o u s e C e n t e r l i n e I n t e r a c t o r S t y l e          //
/////////////////////////////////////////////////////////////////////////////////////

// This class defines a mouse interactor used to create a slice at a selected
// point on a surface centerline.

MouseCenterlineInteractorStyle::MouseCenterlineInteractorStyle()
{
  startSelected = false;
}

void MouseCenterlineInteractorStyle::set_centerlines(Centerlines* centerlines)
{
  centerlines_ = centerlines;
}

void MouseCenterlineInteractorStyle::set_graphics(Graphics* graphics)
{
  graphics_ = graphics;
}

//------------
// OnKeyPress
//------------
//
void MouseCenterlineInteractorStyle::OnKeyPress() 
{
  // Get the keypress.
  vtkRenderWindowInteractor *rwi = this->Interactor;
  std::string key = rwi->GetKeySym();

  // Output the key that was pressed.
  //std::cout << "Pressed " << key << std::endl;

  // Undo. Removes the last slice.
  if (key == "u") {
    auto mesh = graphics_->get_mesh();
    //mesh->UndoSlice();

  // Quit.
  } else if ((key == "Escape") || (key == "q")) {
    exit(0);
  }

  vtkInteractorStyleTrackballCamera::OnKeyPress();
}

//------------------
// SelectCenterline
//------------------
//
void MouseCenterlineInteractorStyle::OnLeftButtonDown() 
//void MouseCenterlineInteractorStyle::SelectCenterline() 
{
  std::cout << "[OnLeftButtonDown] " << std::endl;

  // Get current screen location.
  int* clickPos = this->GetInteractor()->GetEventPosition();
  auto picker = vtkSmartPointer<vtkPropPicker>::New();
  picker->Pick(clickPos[0], clickPos[1], 0, this->GetDefaultRenderer());

  // Get selected actor and world point.
  if (picker->GetActor() == nullptr) {
    vtkInteractorStyleTrackballCamera::OnLeftButtonDown();
    return;
  }
  double* pos = picker->GetPickPosition();
  std::cout << "[OnLeftButtonDown] Pick position (world coordinates) is: " << pos[0] << " " << pos[1] << " " << pos[2] << std::endl;

  // Create a sphere at the picked point.
  if (startSphere == nullptr) {
    startSphere = vtkSmartPointer<vtkSphereSource>::New();
    auto mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
    mapper->SetInputConnection(startSphere->GetOutputPort());
    auto actor = vtkSmartPointer<vtkActor>::New();
    actor->SetMapper(mapper);
    actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
    this->GetDefaultRenderer()->AddActor(actor);
  }

  startSphere->SetCenter(pos[0], pos[1], pos[2]);
  startSphere->SetRadius(0.1);

  double radius = 0.1;
  double inscribedRadius;
  double normal[3], tangent[3], binormal[3], p1[3];
  double planeWidth, origin[3], point1[3], point2[3], vec1[3], vec2[3];
  int index;
  int cellID;

  // Get centerline data at the picked point.
  centerlines_->locate_cell(pos, index, cellID, inscribedRadius, normal);

/*
  startSphere->SetCenter(pos[0], pos[1], pos[2]);
  startSphere->SetRadius(radius);
  //startSphere->SetRadius(radius);
  //
  planeWidth = 4.0*inscribedRadius;
  //planeWidth = 2.0*inscribedRadius;
  vtkMath::Cross(normal, tangent, binormal);
  vtkMath::Normalize(binormal);
  vtkMath::Normalize(tangent);
  //vtkMath::Perpendiculars(normal, vec1, vec2, vtkMath::Pi()/2.0);
  vtkMath::Perpendiculars(normal, vec1, vec2, 0.0);

  for (int i = 0; i < 3; i++) {
    origin[i] = pos[i] - planeWidth/2.0*tangent[i] - planeWidth/2.0*normal[i];
    point1[i] = origin[i] + planeWidth*tangent[i];
    point2[i] = origin[i] + planeWidth*normal[i];
    p1[i] = pos[i] + 0.5*normal[i];
    p1[i] = pos[i] + 0.5*tangent[i];
  }
  startPlane->SetCenter(pos[0], pos[1], pos[2]);
  startPlane->SetNormal(tangent[0], tangent[1], tangent[2]);

  auto mesh = graphics_->get_mesh();
  auto dataName = graphics_->get_data_name();

  // Extract a slice from the mesh.
  //mesh->slice_plane(index, inscribedRadius, cellID, dataName, pos, tangent);

*/
  this->Interactor->GetRenderWindow()->Render();

  // Forward events
  vtkInteractorStyleTrackballCamera::OnLeftButtonDown();
}

vtkStandardNewMacro(MouseCenterlineInteractorStyle);
