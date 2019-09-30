
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
#include <vtkPolyDataMapper.h>
//
#include <vtkSelection.h>
#include <vtkSelectionNode.h>
#include <vtkSphereSource.h>
//
#include <vtkUnstructuredGrid.h>

//----------
// Graphics
//----------
//
Graphics::Graphics()
{
  m_Mesh = nullptr;

  // Add a renderer.
  m_Renderer = vtkSmartPointer<vtkRenderer>::New();
  m_Renderer->SetBackground(1.0, 1.0, 1.0);

  // Add a render window.
  m_RenderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  m_RenderWindow->AddRenderer(m_Renderer);
  m_RenderWindow->SetSize(1000, 1000);

  // Add window interactor to use trackball and intercept key presses.
  //
  m_RenderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  m_RenderWindowInteractor->SetRenderWindow(m_RenderWindow);

  m_InteractionStyle = vtkSmartPointer<MouseInteractorStyle>::New();
  m_InteractionStyle->SetGraphics(this);
  m_RenderWindowInteractor->SetInteractorStyle(m_InteractionStyle);
  m_InteractionStyle->SetDefaultRenderer(m_Renderer);
  m_RenderWindowInteractor->SetInteractorStyle(m_InteractionStyle);

}

Mesh* Graphics::GetMesh()
{
  return m_Mesh;
}
void Graphics::SetMesh(Mesh* mesh)
{
  m_Mesh = mesh;
}
 

void Graphics::Start()
{
  //m_RenderWindowInteractor->Initialize();

  m_RenderWindow->Render();
  m_RenderWindow->SetWindowName("Select Mesh");
  m_RenderWindowInteractor->Start();
}

//----------------
// CreateGeometry 
//----------------
//
vtkSmartPointer<vtkActor> Graphics::CreateGeometry(vtkSmartPointer<vtkPolyData> polyData)
{
  vtkSmartPointer<vtkDataSetMapper> mapper = vtkSmartPointer<vtkDataSetMapper>::New();
  mapper->SetInputData(polyData);
  mapper->ScalarVisibilityOff();
  vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  return actor;
}

//-------------
// AddGeometry
//-------------
//
void Graphics::AddGeometry(vtkSmartPointer<vtkActor> geom)
{
  m_Renderer->AddActor(geom);
}

std::string Graphics::GetDataName() 
{
  return m_DataName;
}

void Graphics::SetDataName(std::string name) 
{
  if (m_Mesh != nullptr) {
    if (m_Mesh->HasData(name)) {
      m_DataName = name;
    } else {
      std::cout << "WARNING: The mesh does not have data named '" << name << "'" << std::endl;
    }
  } else {
      std::cout << "WARNING: The mesh is not set for graphics." << "'" << std::endl;
  }
}

//---------------------
// ShowDuplicateCoords
//---------------------
//
void Graphics::ShowDuplicateCoords() 
{
    for (auto const& pt : m_Mesh->m_DupeCoords) {
        vtkSmartPointer<vtkSphereSource> sphere = vtkSmartPointer<vtkSphereSource>::New();
        sphere->SetCenter(pt[0], pt[1], pt[2]);
        sphere->SetRadius(0.05);
        vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
        mapper->SetInputConnection(sphere->GetOutputPort());
        vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
        actor->SetMapper(mapper);
        actor->GetProperty()->SetColor(0.0, 1.0, 0.0);
        AddGeometry(actor);
    }
}


/////////////////////////////////////////////////////////////////
//            M o u s e I n t e r a c t o r S t y l e          //
/////////////////////////////////////////////////////////////////

MouseInteractorStyle::MouseInteractorStyle()
{
  m_SelectedMapper = vtkSmartPointer<vtkDataSetMapper>::New();
  m_SelectedActor = vtkSmartPointer<vtkActor>::New();
  m_Colors = vtkSmartPointer<vtkNamedColors>::New();

}

void MouseInteractorStyle::SetGraphics(Graphics* graphics)
{
  m_Graphics = graphics;
}

// Process a keyboard press event.
//
void MouseInteractorStyle::OnKeyPress() 
{
  // Get the keypress.
  vtkRenderWindowInteractor *rwi = this->Interactor;
  std::string key = rwi->GetKeySym();
  std::cout << "Pressed key: " << key << std::endl;

  if ((key == "Escape") || (key == "q")) {
    exit(0);
  }
  else if (key == "s") {
    SelectCell();
  }

  // Forward events
  //vtkInteractorStyleTrackballCamera::OnLeftButtonDown();

}

//------------
// SelectCell
//------------
//
void MouseInteractorStyle::SelectCell() 
{
  std::cout << "---------- Select Mesh Cell ----------" << std::endl;
  vtkSmartPointer<vtkNamedColors> colors = vtkSmartPointer<vtkNamedColors>::New();

  // Get the location of the click (in window coordinates)
  int* pos = this->GetInteractor()->GetEventPosition();

  vtkSmartPointer<vtkCellPicker> picker = vtkSmartPointer<vtkCellPicker>::New();
  picker->SetTolerance(0.0005);

  // Pick from this location.
  picker->Pick(pos[0], pos[1], 0, this->GetDefaultRenderer());

  double* worldPosition = picker->GetPickPosition();
  auto cellID = picker->GetCellId();

  if (cellID == -1) {
    return;
  }

  std::cout << "Pick position is: " << worldPosition[0] << " " << worldPosition[1] << " " << worldPosition[2] << endl;
  SelectMesh(cellID);
}

//------------
// SelectMesh
//------------
//
void MouseInteractorStyle::SelectMesh(int cellID)
{ 
  vtkSmartPointer<vtkIdTypeArray> ids = vtkSmartPointer<vtkIdTypeArray>::New();
  ids->SetNumberOfComponents(1);
  ids->InsertNextValue(cellID);

  vtkSmartPointer<vtkSelectionNode> selectionNode = vtkSmartPointer<vtkSelectionNode>::New();
  selectionNode->SetFieldType(vtkSelectionNode::CELL);
  selectionNode->SetContentType(vtkSelectionNode::INDICES);
  selectionNode->SetSelectionList(ids);

  vtkSmartPointer<vtkSelection> selection = vtkSmartPointer<vtkSelection>::New();
  selection->AddNode(selectionNode);

  if (m_Graphics->GetMesh()->IsSurface()) {
    SelectSurfaceMesh(cellID, selection);
  } else {
    SelectSurfaceMesh(cellID, selection);
  }

}

//-------------------
// SelectSurfaceMesh
//-------------------
//
void MouseInteractorStyle::SelectSurfaceMesh(int cellID, vtkSmartPointer<vtkSelection> selection)
{ 
  auto mesh = m_Graphics->GetMesh();
  vtkPolyData* polydata = vtkPolyData::SafeDownCast(mesh->GetMesh());
  auto dataName = m_Graphics->GetDataName();
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
  m_SelectedMapper->SetInputData(selected);
  m_SelectedMapper->ScalarVisibilityOff();
  m_SelectedActor->SetMapper(m_SelectedMapper);
  //selectedActor->GetProperty()->EdgeVisibilityOn();
  //m_SelectedActor->GetProperty()->SetRepresentationToWireframe();
  m_SelectedActor->GetProperty()->SetColor(m_Colors->GetColor3d("Green").GetData());
  m_SelectedActor->GetProperty()->SetLineWidth(4);

  this->Interactor->GetRenderWindow()->GetRenderers()->GetFirstRenderer()->AddActor(m_SelectedActor);
  this->Interactor->GetRenderWindow()->Render();
}


//void MouseInteractorStyle::OnLeftButtonDown()
//{
//}

vtkStandardNewMacro(MouseInteractorStyle);







