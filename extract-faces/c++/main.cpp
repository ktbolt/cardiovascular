#include <string>

#include <vtkArrowSource.h>
#include <vtkCallbackCommand.h>
#include <vtkCellData.h>
#include <vtkCellLocator.h>
#include <vtkCommand.h>
#include <vtkDataSetMapper.h>
#include <vtkDoubleArray.h>
#include <vtkFloatArray.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkInteractorStyleUser.h>
#include <vtkPointData.h>
#include <vtkPointSet.h>
#include <vtkPolyData.h>
#include <vtkPolyDataMapper.h>
#include <vtkPolyDataNormals.h>
#include <vtkPropPicker.h>
#include <vtkProperty.h>
#include <vtkRegularPolygonSource.h>
#include <vtkRenderer.h>
#include <vtkRendererCollection.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkReverseSense.h>
#include <vtkSphereSource.h>
#include <vtkSmartPointer.h>
#include <vtkUnstructuredGrid.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLPolyDataWriter.h>
#include <vtkXMLUnstructuredGridReader.h>

#include <vtkCleanPolyData.h>
#include <vtkFeatureEdges.h>
#include <vtkMath.h>
#include <vtkPolyDataConnectivityFilter.h>

#include <deque>
#include <map>
#include <math.h>
#include <set>

#define nUSE_GRAPHICS

///////////////////////////////////////////////////////////////
//                      G r a p h i c s                      //
///////////////////////////////////////////////////////////////

//----------------------
// MouseInteractorStyle
//----------------------
// Handle mouse events for a trackball interactor.
//
class MouseInteractorStyle : public vtkInteractorStyleTrackballCamera
{
  public:
    static MouseInteractorStyle* New();
    vtkTypeMacro(MouseInteractorStyle, vtkInteractorStyleTrackballCamera);

    MouseInteractorStyle()
    {
      startSelected = false;
    }


    // Need to declare this to prevent Vtk from interpreting pre-defined
    // shortcut keys (e.g. 'e' to exit).
    virtual void OnChar() override { }

    // Process a keyboard press event.
    //
    virtual void OnKeyPress() override
    {
      // Get the keypress.
      vtkRenderWindowInteractor *rwi = this->Interactor;
      std::string key = rwi->GetKeySym();

      // Output the key that was pressed.
      //std::cout << "Pressed " << key << std::endl;
      if (key == "s") {
        startSelected = true;
      } else if (key == "Escape") {
        exit(0);
      }

      vtkInteractorStyleTrackballCamera::OnKeyPress();
    }

    virtual void OnLeftButtonDown() override
    {
      // Pick current screen location.
      //
      int* clickPos = this->GetInteractor()->GetEventPosition();
      vtkSmartPointer<vtkPropPicker> picker = vtkSmartPointer<vtkPropPicker>::New();
      picker->Pick(clickPos[0], clickPos[1], 0, this->GetDefaultRenderer());

      if (picker->GetActor() != nullptr) {
        double* pos = picker->GetPickPosition();
        //std::cout << "Pick position (world coordinates) is: " << pos[0] << " " << pos[1] << " " << pos[2] << std::endl;
        //std::cout << "Picked actor: " << picker->GetActor() << std::endl;

        // Create a sphere.
        if (startSphere == nullptr) {
          startSphere = vtkSmartPointer<vtkSphereSource>::New();
          vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
          mapper->SetInputConnection(startSphere->GetOutputPort());
          vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
          actor->SetMapper(mapper);
          actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
          this->GetDefaultRenderer()->AddActor(actor);
        }

      }

      // Forward events
      vtkInteractorStyleTrackballCamera::OnLeftButtonDown();
    }

  private:
    double startPoint[3], endPoint[3];
    bool startSelected;
    vtkSmartPointer<vtkSphereSource> startSphere = nullptr; 
    vtkSmartPointer<vtkSphereSource> endSphere = nullptr; 

};

vtkStandardNewMacro(MouseInteractorStyle);

// Create a circle
vtkSmartPointer<vtkActor> create_graphics_circle()
{
  vtkSmartPointer<vtkRegularPolygonSource> polygonSource = vtkSmartPointer<vtkRegularPolygonSource>::New();
  polygonSource->SetNumberOfSides(50);
  polygonSource->SetRadius(5);
  polygonSource->SetCenter(0, 0, 0);
  
  vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  mapper->SetInputConnection(polygonSource->GetOutputPort());;
  
  vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  return actor;
}

//--------------------------
// create_graphics_geometry 
//--------------------------
//
vtkSmartPointer<vtkActor> create_graphics_geometry(vtkSmartPointer<vtkPolyData> poly_data)
{
  vtkSmartPointer<vtkDataSetMapper> mapper = vtkSmartPointer<vtkDataSetMapper>::New();
  mapper->SetInputData(poly_data);
  mapper->ScalarVisibilityOff();
  vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  //actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
  return actor;
}

///////////////////////////////////////////////////////////////
//                      E x t r a c t                       //
///////////////////////////////////////////////////////////////

bool cmp(int x, int y)
{
    if (x < y)
        return true;
    else
        return false;
}

//---------------
// add_new_cells
//---------------
//
void add_new_cells(vtkPolyData* surface, vtkDataArray* cell_normals, std::set<int>& edge_cell_ids, std::set<int>& cell_visited, 
    int cell_id, std::deque<int>& new_cells, double feature_angle, std::vector<int>& faces)
{
  //std::cout << std::endl;
  //std::cout << "---------- add_new_cells ---------- " << std::endl;
  //std::cout << "cell_id: " << cell_id << std::endl;
  //std::cout << "new_cells: "; for (int i = 0; i < new_cells.size(); i++) { std::cout << new_cells[i] <<  " "; } std::cout << std::endl; 

  auto cell = surface->GetCell(cell_id);
  cell_visited.insert(cell_id);
  int num_edges = cell->GetNumberOfEdges();
  double cell_normal[3];
  cell_normals->GetTuple(cell_id, cell_normal);
  //auto cell_normal = cell_normals->GetTuple(cell_id);
  //std::cout << "cell normal: " << cell_normal[0] << " " << cell_normal[1] << " " << cell_normal[2] << std::endl;

  for (int i = 0; i < num_edges; i++) { 
     auto edge = cell->GetEdge(i);
     auto edge_ids = edge->GetPointIds();
     int pid1 = edge_ids->GetId(0);
     int pid2 = edge_ids->GetId(1);
     //std::cout << "[add_new_cells] " << std::endl;
     //std::cout << "[add_new_cells] pid1: " << pid1 << "  pid2: " << pid2 << std::endl;
     auto adj_cell_ids = vtkIdList::New();
     surface->GetCellEdgeNeighbors(cell_id, pid1, pid2, adj_cell_ids);
     //std::cout << "[add_new_cells] adj_cell_ids->GetNumberOfIds(): " << adj_cell_ids->GetNumberOfIds() << std::endl;

     for (int j = 0;  j < adj_cell_ids->GetNumberOfIds(); j++) {
       int adj_cell_id = adj_cell_ids->GetId(j);
       //std::cout << "adj_cell_id: " << adj_cell_id << std::endl;
       if (cell_visited.count(adj_cell_id) == 0) { 
         bool add_cell = true;
         if (edge_cell_ids.count(adj_cell_id) != 0) { 
           //std::cout << "*** adj_cell_id in edge_cell_ids " << std::endl;
           double adj_cell_normal[3];
           auto cell_normal = cell_normals->GetTuple(cell_id);
           //auto adj_cell_normal = cell_normals->GetTuple(adj_cell_id);
           cell_normals->GetTuple(adj_cell_id, adj_cell_normal);
           //std::cout << "cell normal: " << cell_normal[0] << " " << cell_normal[1] << " " << cell_normal[2] << std::endl;
           //std::cout << "adj cell normal: " << adj_cell_normal[0] << " " << adj_cell_normal[1] << " " << adj_cell_normal[2] << std::endl;
           //double dp = cell_normal[0]*adj_cell_normal[0] + cell_normal[1]*adj_cell_normal[1] + cell_normal[2]*adj_cell_normal[2];
           double dp = vtkMath::Dot(cell_normal, adj_cell_normal);
           //std::cout << "dp: " << dp << std::endl;
           if (dp < feature_angle) {
             add_cell = false;
             //std::cout << "[add_new_cells] don't add new cell " << std::endl;
           }
         }

         if (add_cell) { 
           //std::cout << "+++ add new cell " << adj_cell_id << std::endl;
           //new_cells.push_front(adj_cell_id);
           new_cells.push_back(adj_cell_id);
           cell_visited.insert(cell_id);
         }

       }
     }
  }

}

//--------------------------------
// extract_surface_boundary_faces
//--------------------------------
// Extract the surface boundary faces and set the ModelFaceID cell data array.
//
void extract_surface_boundary_faces(vtkPolyData* surface, double feature_angle)
{
  // Compute edge features separating surface cells by the given angle.
  //
  std::cout << "Compute feature edges ..." << std::endl;
  auto feature_edges = vtkFeatureEdges::New();
  feature_edges->SetInputData(surface);
  feature_edges->BoundaryEdgesOff();
  feature_edges->ManifoldEdgesOff();
  feature_edges->NonManifoldEdgesOff();
  feature_edges->FeatureEdgesOn();
  feature_edges->SetFeatureAngle(feature_angle);
  feature_edges->Update();

  auto boundary_edges = feature_edges->GetOutput();
  auto clean_filter = vtkCleanPolyData::New();
  clean_filter->SetInputData(boundary_edges);
  clean_filter->Update();
  auto cleaned_edges = clean_filter->GetOutput();

  auto conn_filter = vtkPolyDataConnectivityFilter::New();
  conn_filter->SetInputData(cleaned_edges);
  conn_filter->SetExtractionModeToSpecifiedRegions();
  std::vector<vtkPolyData*> boundary_edge_components; 
  int edge_id = 0;

  while (true) {
    conn_filter->AddSpecifiedRegion(edge_id);
    conn_filter->Update();
    auto component = vtkPolyData::New();
    component->DeepCopy(conn_filter->GetOutput());
    if (component->GetNumberOfCells() <= 0) {
      break;
    }
    boundary_edge_components.push_back(component);
    conn_filter->DeleteSpecifiedRegion(edge_id);
    edge_id += 1;
  }

  std::cout << "Number of edges: " << edge_id << std::endl;

  // Identify the cells incident to the feature edges.
  //
  std::cout << "Identify edge cells ..." << std::endl;

  // Create a set of edge nodes.
  std::set<int> edge_nodes; 
  for (auto const edge : boundary_edge_components) {
    int edge_num_points = edge->GetNumberOfPoints();
    vtkDataArray* edge_node_ids = edge->GetPointData()->GetArray("GlobalNodeID");
    //std::cout << "edge nodes: " << std::endl;
    for (int i = 0; i < edge_num_points; i++) {
      int nid = edge_node_ids->GetTuple1(i);
      //std::cout << nid << " " << std::endl;
      //int nid = edge_node_ids->GetValue(i);
      edge_nodes.insert(nid);
    }
  }

  std::cout << "Number of edge nodes: " << edge_nodes.size() << std::endl;

  // Create a set of cell IDs incident to the edge nodes.
  auto surf_points = surface->GetPoints();
  int num_cells = surface->GetNumberOfCells();
  auto surf_node_ids = surface->GetPointData()->GetArray("GlobalNodeID");
  std::set<int> edge_cell_ids;
  std::cout << "Number of cells: " << num_cells << std::endl;

  for (int i = 0; i < num_cells; i++) {
    auto cell = surface->GetCell(i);
    auto cell_pids = cell->GetPointIds();
    int num_ids = cell_pids->GetNumberOfIds();
    //std::cout << "Cell: " << i << "  ";
    //for (int j = 0; j < num_ids; j++) {
      //int pid = surf_node_ids->GetTuple1(cell_pids->GetId(j));
      //std::cout << pid << " " ;
    //}
    //std::cout << std::endl; 
    for (int j = 0; j < num_ids; j++) {
      int pid = surf_node_ids->GetTuple1(cell_pids->GetId(j));
      if (edge_nodes.count(pid) != 0) { 
        //std::cout << "add cells: " << i << std::endl;
        edge_cell_ids.insert(i);
        break;
      }
    }
  }

  std::cout << "Number of edge cell IDs: " << edge_cell_ids.size() << std::endl;

  // Identify boundary faces using edge cells.
  //
  std::set<int> cell_visited;
  auto cell_normals = surface->GetCellData()->GetArray("Normals");
  double feature_angle_rad = cos(M_PI/180.0 * feature_angle);
  std::cout << "feature_angle_rad: " << feature_angle_rad << std::endl;
  std::deque<int> new_cells;
  std::map<int,std::vector<int>> faces;
  int face_id = 0;
  std::cout << "Traverse edge cells ..." << std::endl;

  for (auto cell_id : edge_cell_ids) {
    if (cell_visited.count(cell_id) != 0) {
      continue;
    }
   
    add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle_rad, faces[face_id]);
    faces[face_id].push_back(cell_id);

    while (new_cells.size() != 0) { 
      int new_cell_id = new_cells.back();
      new_cells.pop_back();
      if (cell_visited.count(new_cell_id) == 0) {
        faces[face_id].push_back(new_cell_id);
      }
      add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, new_cell_id, new_cells, feature_angle_rad, faces[face_id]);
    }
    face_id += 1;
  }

  // Check that we got all of the cells.
  /*
  std::cout << std::endl;
  std::cout << "Number of cells visited: " << cell_visited.size() << std::endl;
  std::cout << "Number of faces: " << face_id << std::endl;
  std::cout << "Faces: " << std::endl;
  int faces_size = 0;
  for (auto const& face : faces) { 
    faces_size += face.second.size();
  }
  std::cout << "Number of faces cells: " << faces_size << std::endl;
  */

  // Add the 'ModelFaceID' cell data array identifying each cell with a face ID.
  auto face_ids_data = vtkIntArray::New();
  face_ids_data->SetNumberOfValues(num_cells);
  face_ids_data->SetName("ModelFaceID");
  for (auto const& face : faces) { 
    face_id = face.first;
    auto cell_list = face.second;
    for (auto cell_id : cell_list) { 
      face_ids_data->SetValue(cell_id, face_id+1);
    }
  }
  surface->GetCellData()->AddArray(face_ids_data);

  // Write the surface with the 'ModelFaceID' cell data array.
  auto writer = vtkXMLPolyDataWriter::New();
  writer->SetFileName("boundary.vtp");
  writer->SetInputData(surface);
  writer->Write();
}

//----------------
// read_poly_data 
//----------------
//
vtkSmartPointer<vtkPolyData> read_poly_data(const std::string fileName) 
{
  vtkSmartPointer<vtkPolyData> polydata = vtkSmartPointer<vtkPolyData>::New();
  vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();
  polydata->DeepCopy(reader->GetOutput());

  auto normals = vtkPolyDataNormals::New();
  normals->SetInputData(polydata);
  normals->SplittingOff();
  normals->ComputeCellNormalsOn();
  normals->ComputePointNormalsOn();
  normals->ConsistencyOn();
  normals->AutoOrientNormalsOn();
  normals->Update();

  auto surface = normals->GetOutput();
  surface->BuildLinks();

  return surface;
}

//-------
// main 
//-------

int main(int argc, char* argv[])
{
  vtkObject::GlobalWarningDisplayOff();

  // Parse command line arguments
  if (argc != 3) {
    std::cout << "Usage: " << argv[0] << " SURACE_FILE_NAME(.vtp)  FEATURE_ANGLE" << std::endl;
    return EXIT_FAILURE;
  }

  std::string surf_file_name = argv[1];
  double feature_angle = atof(argv[2]);

  // Read the surface.
  //
  auto surface = read_poly_data(surf_file_name);
  vtkIdType numSurfVerts = surface->GetNumberOfPoints();
  vtkIdType numPolygons = surface->GetNumberOfPolys();
  std::cout << "Surface: " << std::endl;
  std::cout << "   Number of vertices " << numSurfVerts << std::endl;
  std::cout << "   Number of polygons " << numPolygons << std::endl;

  // Extract boundary faces.
  extract_surface_boundary_faces(surface, feature_angle);

  #ifdef USE_GRAPHICS
  auto gr_surf = create_graphics_geometry(surface);
  gr_surf->GetProperty()->SetColor(0.8, 0.8, 0.8);
  gr_surf->GetProperty()->SetOpacity(0.5);
  //gr_surf->GetProperty()->SetRepresentationToWireframe();
  //gr_surf->GetProperty()->FrontfaceCullingOn();
  //gr_surf->GetProperty()->BackfaceCullingOn();
  gr_surf->PickableOff();

  // Add a renderer.
  auto renderer = vtkSmartPointer<vtkRenderer>::New();
  renderer->AddActor(gr_lines);
  renderer->AddActor(gr_surf);
  renderer->SetBackground(1.0, 1.0, 1.0); 

  // Add a render window.
  autto renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(1600, 1400); 

  // Add window interactor to use trackball and intercept key presses.
  auto renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  renderWindowInteractor->SetRenderWindow(renderWindow);
  auto style = vtkSmartPointer<MouseInteractorStyle>::New();
  style->AddClEdit(clEdit);
  renderWindowInteractor->SetInteractorStyle(style);
  style->SetDefaultRenderer(renderer);
  renderWindowInteractor->SetInteractorStyle(style);

  renderWindowInteractor->Initialize();
  renderWindowInteractor->Start();

  #endif

  return EXIT_SUCCESS;
}
