#include <string>

#include <vtkActor.h>
#include <vtkDataSetMapper.h>
#include <vtkDoubleArray.h>
#include <vtkFloatArray.h>
#include <vtkGeometryFilter.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkInteractorStyleUser.h>
#include <vtkLine.h>
#include <vtkLineSource.h>
#include <vtkPlaneSource.h>
#include <vtkPointData.h>
#include <vtkPoints.h>
#include <vtkPointSet.h>
#include <vtkPolyData.h>
#include <vtkPolyLine.h>
#include <vtkTransformPolyDataFilter.h>
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
#include <vtkTriangleFilter.h>
#include <vtkUnstructuredGrid.h>
#include <vtkVertexGlyphFilter.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLPolyDataWriter.h>
#include <vtkXMLUnstructuredGridReader.h>

vtkSmartPointer<vtkActor> create_points_geometry(int numPts, double* pts);

//----------
// LineData
//----------
//
class LineData 
{
  public:
    LineData(int numCoords, double* lineCoords);
    bool FindPoint(double* point, double projPoint[3], double& minDist, int segNum=-1);
    int numCoords_;
    double* lineCoords_;
    double* lineVecs_;
    double* lineWidth_;
};

LineData::LineData(int numCoords, double* lineCoords) 
{
  numCoords_ = numCoords;
  lineCoords_ = lineCoords;
  lineVecs_ = new double[3*numCoords];
  lineWidth_ = new double[numCoords];
  for (int i = 0; i < numCoords-1; i++) {
      double dv[3];
      double dp = 0.0;
      for (int j = 0; j < 3; j++) {
          dv[j] = lineCoords_[3*(i+1)+j] - lineCoords_[3*i+j];
          dp += dv[j] * dv[j];
      }
      lineWidth_[i] = sqrt(dp);
      for (int j = 0; j < 3; j++) {
          lineVecs_[3*i+j] = dv[j] / lineWidth_[i]; 
      }
  }
};    

bool
LineData::FindPoint(double* point, double projPoint[3], double& minDist, int segNum)
{
  double testPt[3];
  bool foundPt = false;
  minDist = 1e6;
  for (int i = 0; i < numCoords_-1; i++) {
      double dp = 0.0;
      double width = lineWidth_[i];
      for (int j = 0; j < 3; j++) {
          dp += (point[j] - lineCoords_[3*i+j]) * lineVecs_[3*i+j];
      }
/*
      if (segNum == 3) {
          std::cout << "[LineData::FindPoint]  " << std::endl; 
          std::cout << "[LineData::FindPoint] i: " << i << std::endl; 
          std::cout << "[LineData::FindPoint] dp: " << dp << std::endl; 
          std::cout << "[LineData::FindPoint] width: " << width << std::endl; 
      }
*/
      if ((dp >= 0.0) && (dp <= width)) {
          double dist = 0.0;
          for (int j = 0; j < 3; j++) {
              testPt[j] = lineCoords_[3*i+j] + dp*lineVecs_[3*i+j];
              dist += (point[j]-testPt[j]) * (point[j]-testPt[j]);
          }
          dist = sqrt(dist);
          // std::cout << "[LineData::FindPoint] dist: " << dist << std::endl; 
          if (dist < minDist) {
              for (int j = 0; j < 3; j++) {
                  projPoint[j] = testPt[j];
              }
              minDist = dist;
              std::cout << "[LineData::FindPoint] i: " << i << std::endl; 
              std::cout << "[LineData::FindPoint] Found point at distance: " << dist << std::endl; 
              foundPt = true;
          }
      }
  }

  return foundPt;
}

//-------------
// ProjectMesh
//-------------
//
class ProjectMesh 
{
  public:
    ProjectMesh(vtkSmartPointer<vtkUnstructuredGrid> mesh, vtkSmartPointer<vtkPolyData> centerlines, vtkSmartPointer<vtkRenderer> renderer);
    void Project();
    bool ProjectPoint(double* point, double projPoint[3]);

    vtkSmartPointer<vtkUnstructuredGrid> mesh_; 
    vtkSmartPointer<vtkPolyData> centerlines_;
    double *coordinates_;
    std::vector<LineData*> lineSegments_;
    vtkSmartPointer<vtkRenderer> renderer_;
};

ProjectMesh::ProjectMesh(vtkSmartPointer<vtkUnstructuredGrid> mesh, vtkSmartPointer<vtkPolyData> centerlines, vtkSmartPointer<vtkRenderer> renderer) : 
      mesh_(mesh), centerlines_(centerlines), renderer_(renderer)
{
  // Create an array of mesh coordinates.
  vtkIdType numNodes = mesh_->GetNumberOfPoints();
  std::cout << "Mesh: " << std::endl;
  std::cout << "   Number of nodes: " << numNodes << std::endl;
  coordinates_ = new double[3*numNodes];
  double point[3];
  auto points = mesh_->GetPoints();
  for (int i = 0; i < numNodes; i++) {
      points->GetPoint(i, point);
      coordinates_[3*i] = point[0];
      coordinates_[3*i+1] = point[1];
      coordinates_[3*i+2] = point[2];
  }

  // Create an array of line segments.
  vtkIdType numPoints = centerlines_->GetNumberOfPoints();
  auto linePoints = centerlines_->GetPoints();
  vtkIdType numLines = centerlines_->GetNumberOfLines();
  std::cout << "Centerlines: " << std::endl;
  std::cout << "   Number of points: " << numPoints << std::endl;
  std::cout << "   Number of lines " << numLines << std::endl;

  centerlines_->GetLines()->InitTraversal();
  vtkSmartPointer<vtkIdList> idList = vtkSmartPointer<vtkIdList>::New();
  int n = 1;
  int totalNumPoints = 0;
  while (centerlines_->GetLines()->GetNextCell(idList)) {
      std::cout << "---------- Line " << n << "---------- " << std::endl;
      std::cout << "  Number of points: " << idList->GetNumberOfIds() << std::endl;
      int numIDs = idList->GetNumberOfIds();
      double* lineCoords = new double[3*numIDs];
      int numCoords = 0;
      for (vtkIdType pointId = 0; pointId < idList->GetNumberOfIds(); pointId++) {
          int id = idList->GetId(pointId);
          linePoints->GetPoint(id, point);
          lineCoords[3*numCoords] = point[0];
          lineCoords[3*numCoords+1] = point[1];
          lineCoords[3*numCoords+2] = point[2];
          totalNumPoints += 1;
          numCoords += 1;
      }

      if (n == 3) {
          auto actor = create_points_geometry(numCoords, lineCoords);
          renderer_->AddActor(actor);
      }

      std::cout << "  Number of coords: " << numCoords << std::endl;
      lineSegments_.push_back(new LineData(numCoords, lineCoords));
      n += 1;
  }
  std::cout << "  totalNumPoints: " << totalNumPoints << std::endl;
}

//---------
// project
//---------
//
void
ProjectMesh::Project()
{
  std::cout << "=================== ProjectMesh::project ====================" << std::endl;
  vtkIdType numNodes = mesh_->GetNumberOfPoints();
  int numFoundPts = 0;
  double projPoint[3];
  double minSegDist = 1e6;
  for (int i = 0; i < numNodes; i++) {
      double mpt[3] = { coordinates_[3*i], coordinates_[3*i+1], coordinates_[3*i+2] };
      double testPoint[3];
      double minDist;

      for (auto lineData : lineSegments_) {
          if (lineData->FindPoint(mpt, testPoint, minDist)) {
              numFoundPts += 1;
              if (minDist < minSegDist) {
                  minSegDist = minDist;
                  projPoint[0] = testPoint[0];
                  projPoint[1] = testPoint[1];
                  projPoint[2] = testPoint[2];
              }
          }
      }
  }
  std::cout << "[ProjectMesh::project] Number of points found: " << numFoundPts << std::endl;
}

bool 
ProjectMesh::ProjectPoint(double* point, double projPoint[3])
{
  /*
  point[0] = 6.42792;
  point[1] =  2.78067;
  point[2] = -15.5939;
  */
  std::cout << "[ProjectMesh::ProjectPoint] ----------------- ProjectPoint ------------ " << std::endl;
  bool foundPt = false;
  double minSegDist = 1e6;
  double minDist;
  double testPoint[3];
  int segNum = 1;
  for (auto lineData : lineSegments_) {
      std::cout << "[ProjectMesh::ProjectPoint] ---------- Seg " << segNum << " ----------" << std::endl;
      if (lineData->FindPoint(point, testPoint, minDist, segNum)) {
          foundPt = true;
          std::cout << "[ProjectMesh::ProjectPoint]   minDist: " << minDist << std::endl;
          std::cout << "[ProjectMesh::ProjectPoint]   testPoint: " << testPoint[0] << "  " << testPoint[1] << "  " << testPoint[2] << std::endl;
          if (minDist < minSegDist) {
              minSegDist = minDist;
              projPoint[0] = testPoint[0];
              projPoint[1] = testPoint[1];
              projPoint[2] = testPoint[2];
          }
      }
      segNum += 1;
  }
  std::cout << "[ProjectMesh::ProjectPoint]   minSegDist: " << minSegDist << std::endl;
  std::cout << "[ProjectMesh::ProjectPoint]   projPoint: " << projPoint[0] << "  " << projPoint[1] << "  " << projPoint[2] << std::endl;
  return foundPt;
}

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
    ProjectMesh* projectMesh_;

    MouseInteractorStyle()
    {
      startSelected = false;
    }

    void AddProjectMesh(ProjectMesh* projectMesh)
    {
      projectMesh_ = projectMesh;
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
      } else if (key == "e") {
        startSelected = false;
      } else if (key == "p") {
        projectMesh_->Project();
      } else if (key == "q") {
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
        std::cout << std::endl;
        std::cout << "Pick position (world coordinates) is: " << pos[0] << " " << pos[1] << " " << pos[2] << std::endl;
        std::cout << "Picked actor: " << picker->GetActor() << std::endl;
        double projPoint[3];
        if (projectMesh_->ProjectPoint(pos, projPoint)) {
            std::cout << "Projected point found : " << std::endl;
            auto lineSource = vtkSmartPointer<vtkLineSource>::New();
            lineSource->SetPoint1(pos);
            lineSource->SetPoint2(projPoint);
            lineSource->Update();
            auto mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
            mapper->SetInputConnection(lineSource->GetOutputPort());
            auto actor = vtkSmartPointer<vtkActor>::New();
            actor->SetMapper(mapper);
            actor->GetProperty()->SetColor(1.0, 0.0, 1.0);
            actor->GetProperty()->SetLineWidth(4.0);
            this->GetDefaultRenderer()->AddActor(actor);
        }

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

        if (startPlane == nullptr) {
          startPlane = vtkSmartPointer<vtkPlaneSource>::New();
          vtkSmartPointer<vtkPolyDataMapper> pmapper = vtkSmartPointer<vtkPolyDataMapper>::New();
          pmapper->SetInputConnection(startPlane->GetOutputPort());
          vtkSmartPointer<vtkActor> startPlaneActor = vtkSmartPointer<vtkActor>::New();
          startPlaneActor->SetMapper(pmapper);
          startPlaneActor->GetProperty()->SetColor(1.0, 0.0, 0.0);
          // [DaveP] uncomment to show plane.
          // this->GetDefaultRenderer()->AddActor(startPlaneActor);
        }

        double radius = 0.1;
        double inscribedRadius;
        double normal[3], tangent[3], binormal[3], p1[3];
        double planeWidth, origin[3], point1[3], point2[3], vec1[3], vec2[3];
        int index;

        // Get centerline data at the picked point.
        //clEdit_.locate_cell(pos, index, inscribedRadius, normal, tangent);

        if (!startSelected) { 
          startSphere->SetCenter(pos[0], pos[1], pos[2]);
          startSphere->SetRadius(radius);
          //startSphere->SetRadius(radius);
          //
          planeWidth = 2.0*inscribedRadius;
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
          /*
          startPlane->SetOrigin(origin[0], origin[1], origin[2]);
          startPlane->SetPoint1(point1[0], point1[1], point1[2]);
          startPlane->SetPoint2(point2[0], point2[1], point2[2]);
          */
          /*
          */
          startPlane->SetCenter(pos[0], pos[1], pos[2]);
          startPlane->SetNormal(tangent[0], tangent[1], tangent[2]);

        } else {
          if (endSphere == nullptr) {
            endSphere = vtkSmartPointer<vtkSphereSource>::New();
            vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
            mapper->SetInputConnection(endSphere->GetOutputPort());
            vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
            actor->SetMapper(mapper);
            actor->GetProperty()->SetColor(0.0, 0.0, 0.0);
            this->GetDefaultRenderer()->AddActor(actor);
          }
          if (endPlane == nullptr) {
            endPlane = vtkSmartPointer<vtkPlaneSource>::New();
            vtkSmartPointer<vtkPolyDataMapper> emapper = vtkSmartPointer<vtkPolyDataMapper>::New();
            emapper->SetInputConnection(endPlane->GetOutputPort());
            vtkSmartPointer<vtkActor> endPlaneActor = vtkSmartPointer<vtkActor>::New();
            endPlaneActor->SetMapper(emapper);
            endPlaneActor->GetProperty()->SetColor(0.0, 1.0, 0.0);
            this->GetDefaultRenderer()->AddActor(endPlaneActor);
          }

          endSphere->SetCenter(pos[0], pos[1], pos[2]);
          endSphere->SetRadius(radius);
          endPlane->SetCenter(pos[0], pos[1], pos[2]);
          endPlane->SetNormal(tangent[0], tangent[1], tangent[2]);
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
    vtkSmartPointer<vtkPlaneSource> startPlane = nullptr; 
    vtkSmartPointer<vtkPlaneSource> endPlane = nullptr; 
    vtkSmartPointer<vtkLineSource> line; 

};

vtkStandardNewMacro(MouseInteractorStyle);

//------------------------
// create_points_geometry
//------------------------
//
vtkSmartPointer<vtkActor> create_points_geometry(int numPts, double* pts)
{
  auto points = vtkSmartPointer<vtkPoints>::New();

  for (int i = 0; i < numPts; i++) {
      points->InsertNextPoint(pts[3*i], pts[3*i+1], pts[3*i+2]); 
  }
  auto pointsPolydata = vtkSmartPointer<vtkPolyData>::New();
  pointsPolydata->SetPoints(points);
  auto vertexFilter = vtkSmartPointer<vtkVertexGlyphFilter>::New();
  vertexFilter->SetInputData(pointsPolydata);
  vertexFilter->Update();

  auto polydata = vtkSmartPointer<vtkPolyData>::New();
  polydata->ShallowCopy(vertexFilter->GetOutput());

  auto mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  mapper->SetInputData(polydata);

  auto actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  actor->GetProperty()->SetPointSize(4);
  actor->GetProperty()->SetColor(0.0, 1.0, 0.0);

  return actor;
}

//--------------------------
// create_graphics_geometry 
//--------------------------
//
vtkSmartPointer<vtkActor> create_graphics_geometry(vtkSmartPointer<vtkPolyData> poly_data)
{
  auto mapper = vtkSmartPointer<vtkDataSetMapper>::New();
  mapper->SetInputData(poly_data);
  mapper->ScalarVisibilityOff();
  auto actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  //actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
  return actor;
}

//----------------
// read_poly_data 
//----------------

vtkSmartPointer<vtkPolyData> read_poly_data(const std::string fileName) 
{
  vtkSmartPointer<vtkPolyData> polydata = vtkSmartPointer<vtkPolyData>::New();
  vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();
  polydata->DeepCopy(reader->GetOutput());
  return polydata;
}

//---------------
// read_vtu_data 
//---------------

void 
read_vtu_data(const std::string fileName, vtkSmartPointer<vtkUnstructuredGrid>& mesh, vtkSmartPointer<vtkPolyData>& surface)
{
  auto reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();
  mesh = reader->GetOutput();

  // Convert mesh to polydata.
  auto geometryFilter = vtkSmartPointer<vtkGeometryFilter>::New();
  geometryFilter->SetInputData(mesh);
  geometryFilter->Update(); 
  auto meshPolyData = geometryFilter->GetOutput();

  auto triangleFilter = vtkSmartPointer<vtkTriangleFilter>::New();
  triangleFilter->SetInputData(meshPolyData);
  triangleFilter->Update();
  surface = triangleFilter->GetOutput();
}

//-------
// main 
//-------

int main(int argc, char* argv[])
{
  vtkObject::GlobalWarningDisplayOff();

  // Parse command line arguments
  if (argc != 3) {
    std::cout << "Usage: " << argv[0] << " SURACE_FILE_NAME(.vtp)  CENTERLINE_FILE_NAME (.vtp)" << std::endl;
    return EXIT_FAILURE;
  }

  // Read and display surface.
  //
  std::string mesh_file_name = argv[1];
  vtkSmartPointer<vtkUnstructuredGrid> mesh; 
  vtkSmartPointer<vtkPolyData> surface;
  read_vtu_data(mesh_file_name, mesh, surface);
  //tkIdType numNodes = mesh->GetNumberOfPoints();
  //std::cout << "Mesh: " << std::endl;
  //std::cout << "   Number of nodes: " << numNodes << std::endl;
  auto gr_surf = create_graphics_geometry(surface);
  gr_surf->GetProperty()->SetColor(0.8, 0.8, 0.8);
  gr_surf->GetProperty()->SetOpacity(0.5);
  //gr_surf->GetProperty()->SetRepresentationToWireframe();
  //gr_surf->GetProperty()->FrontfaceCullingOn();
  //gr_surf->GetProperty()->BackfaceCullingOn();
  //gr_surf->PickableOff();

  // Read and display centerlines.
  //
  std::string cl_file_name = argv[2];
  auto lines = read_poly_data(cl_file_name);
  //vtkIdType numLineVerts = lines->GetNumberOfPoints();
  //vtkIdType numLines = lines->GetNumberOfLines();
  //std::cout << "Centerlines: " << std::endl;
  //std::cout << "   Number of vertices " << numLineVerts << std::endl;
  //std::cout << "   Number of lines " << numLines << std::endl;
  // Create lines graphics geometry.
  auto gr_lines = create_graphics_geometry(lines);
  gr_lines->GetProperty()->SetColor(1.0, 0.0, 0.0);
  gr_lines->GetProperty()->SetLineWidth(4.0);

  // Add a renderer.
  vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
  renderer->AddActor(gr_lines);
  renderer->AddActor(gr_surf);
  renderer->SetBackground(1.0, 1.0, 1.0); 

  // Add a render window.
  vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(1600, 1400); 

  // Create objext used to project mesh nodes onto centerline.
  auto projectMesh = new ProjectMesh(mesh, lines, renderer);

  // Add window interactor to use trackball and intercept key presses.
  //
  vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  renderWindowInteractor->SetRenderWindow(renderWindow);
  vtkSmartPointer<MouseInteractorStyle> style = vtkSmartPointer<MouseInteractorStyle>::New();
  renderWindowInteractor->SetInteractorStyle(style);
  style->SetDefaultRenderer(renderer);
  style->AddProjectMesh(projectMesh);
  renderWindowInteractor->SetInteractorStyle(style);

  renderWindowInteractor->Initialize();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
