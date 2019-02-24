#include <string>

#include <vtkActor.h>
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
#include <vtkLine.h>
#include <vtkLineSource.h>
#include <vtkPlaneSource.h>
#include <vtkPointData.h>
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
#include <vtkUnstructuredGrid.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLPolyDataWriter.h>
#include <vtkXMLUnstructuredGridReader.h>

//----------------
// CenterLineEdit 
//----------------

class CenterLineEdit 
{
  public:
    CenterLineEdit() {}

    CenterLineEdit(vtkSmartPointer<vtkPolyData> surface, vtkSmartPointer<vtkPolyData> lines, std::string clFileName) : 
        surface(surface), centerlines(lines), clFileName(clFileName)
    {
      create_cell_locator();
      numCenterLineVerts = lines->GetNumberOfPoints();
      vtkIdType numberOfPointArrays = lines->GetPointData()->GetNumberOfArrays();
      std::cout << "[CenterLineEdit] " << std::endl;
      std::cout << "[CenterLineEdit] Centerlines: " << std::endl;
      std::cout << "[CenterLineEdit]   Number of PointData arrays: " << numberOfPointArrays << std::endl;
      std::cout << "[CenterLineEdit]   PointData arrays: " << std::endl;

      for(vtkIdType i = 0; i < numberOfPointArrays; i++) {
        int dataTypeID = lines->GetPointData()->GetArray(i)->GetDataType();  // float, double (11), etc.
        auto arrayName = std::string(lines->GetPointData()->GetArrayName(i));
        std::cout << "[CenterLineEdit] Array " << i << ": " << arrayName << " (type: " << dataTypeID << ")" << std::endl;
 
        if (arrayName == "MaximumInscribedSphereRadius") { 
          std::cout << "[CenterLineEdit]     Have MaximumInscribedSphereRadius data" << std::endl;
          radiusData = vtkDoubleArray::SafeDownCast(lines->GetPointData()->GetArray(arrayName.c_str()));
        } 

        if (arrayName == "ParallelTransportNormals") { 
          std::cout << "[CenterLineEdit]     Have ParallelTransportNormals data" << std::endl;
          normalData = vtkDoubleArray::SafeDownCast(lines->GetPointData()->GetArray(arrayName.c_str()));
        }

        // Abscissa data measures the distances along the centerline.
        if (arrayName == "Abscissas") { 
          std::cout << "[CenterLineEdit]     Have Abscissas data" << std::endl;
          abscissaData = vtkDoubleArray::SafeDownCast(lines->GetPointData()->GetArray(arrayName.c_str()));
        }
      }

      // Set material IDs.
      materialID = 1;
      for (int i = 0; i < numCenterLineVerts; i++) {
        centerLineMaterialIDs.push_back(i);
        //centerLineMaterialIDs.push_back(materialID);
      } 
    } 

    //---------------------
    // create_cell_locator
    //---------------------
    // Create a vtkCellLocator to find picked points in centerlines.
    //
    void create_cell_locator()
    {
      cellLocator = vtkSmartPointer<vtkCellLocator>::New();
      cellLocator->SetDataSet(centerlines);
      cellLocator->BuildLocator();

      pointSet = vtkSmartPointer<vtkPolyData>::New();
      pointSet->SetPoints(centerlines->GetPoints());
    }

    //-------------
    // locate_cell
    //-------------
    // Locate the given point in centerlines.
    //
    void locate_cell(double point[3], int& index, double& radius, double normal[3], double tangent[3])
    {
      auto msg = "[locate_cell] ";
      std::cout << msg << std::endl;
      std::cout << msg << "Point: " << point[0] << " " << point[1] << " " << point[2] << std::endl;

      // Find the point in centerlines that is closest to the selected point.
      // 
      // Note that cellLocator->FindClosestPoint(point, closestPoint, cellId, subId, closestPointDist2) 
      // does not return the index of the selected point in centerlines in the returned variable 'subId'. 
      // In fact, it is not ducumented and no one seems to know what is represents!
      //
      double closestPoint[3];
      double closestPointDist2; 
      vtkIdType cellId; 
      int subId; 
      cellLocator->FindClosestPoint(point, closestPoint, cellId, subId, closestPointDist2);
      index = pointSet->FindPoint(point);
      std::cout << msg << "Closest point: " << closestPoint[0] << " " << closestPoint[1] << " " << closestPoint[2] << std::endl;
      std::cout << msg << "Distance to closest point: " << closestPointDist2 << std::endl;
      std::cout << msg << "CellId: " << cellId << std::endl;
      std::cout << msg << "Index: " << index << std::endl;
      std::cout << msg << "Material ID: " << centerLineMaterialIDs[index] << std::endl;

      if (radiusData) {
        radius = radiusData->GetValue(index);
        std::cout << msg << "Radius: " << radius << std::endl;
      }

      if (normalData) {
        normalData->GetTuple(index, normal);
        std::cout << msg << "Normal: " << normal[0] << " " << normal[1] << " " << normal[2] << std::endl;
      }

      // Abscissas measure the distances along the centerline.
      if (abscissaData) {
        auto distance = abscissaData->GetValue(index);
        std::cout << msg << "Distance: " << distance << std::endl;
      }

      // Compute tangent.
      //
      double p1[3], p2[3], v[3];
      centerlines->GetPoint(index, p1);
      centerlines->GetPoint(index+2, p2);
      vtkMath::Subtract(p2, p1,tangent);
      vtkMath::Normalize(tangent);
      std::cout << msg << "Tangent " << tangent[0] << " " << tangent[1] << " " << tangent[2] << std::endl;
    }

    void write_centerline()
    {
      std::cout << "[write_centerline] " << std::endl;

      // Construct Get name of file to store material IDs.
      //
      size_t loc = clFileName.find_last_of(".");
      std::string name;
      std::string ext; clFileName.substr(loc, clFileName.size() - loc);
      if (loc != std::string::npos) {
        name = clFileName.substr(0, loc);
        ext  = clFileName.substr(loc, clFileName.size() - loc);
      } else {
        name = clFileName;
        ext  = "";
      }
      std::string materialFileName = name + "_material" + ext;
      std::cout << "[write_centerline] Material file name " << materialFileName << std::endl;

      // Create new poly data.
      //
      vtkSmartPointer<vtkPolyData> newPolyData = vtkSmartPointer<vtkPolyData>::New();
      // Copy points.
      vtkSmartPointer<vtkPoints> newPoints = vtkSmartPointer<vtkPoints>::New();
      auto points = centerlines->GetPoints();
      for(vtkIdType i = 0; i < points->GetNumberOfPoints(); i++) {
        double p[3];
        points->GetPoint(i,p);
        newPoints->InsertNextPoint(p);
      }
      newPolyData->SetPoints(newPoints);
      // Copy cells.
      vtkSmartPointer<vtkCellArray> newCells = vtkSmartPointer<vtkCellArray>::New();
      for (vtkIdType i = 0; i < centerlines->GetNumberOfCells(); i++) {
        //std::cout << "[write_centerline] Cell " << i << std::endl;
        vtkCell* cell = centerlines->GetCell(i);
        vtkPolyLine* polyLine = dynamic_cast<vtkPolyLine*>(cell);
        vtkSmartPointer<vtkPolyLine> newPolyLine = vtkSmartPointer<vtkPolyLine>::New();
        auto ids = polyLine->GetPointIds();
        //std::cout << "[write_centerline]   IDs: ";
        newPolyLine->GetPointIds()->SetNumberOfIds(ids->GetNumberOfIds());
        for (vtkIdType j = 0; j < ids->GetNumberOfIds(); j++) {
          auto id = ids->GetId(j);
          //std::cout << j << ":" << id << ",";
          newPolyLine->GetPointIds()->SetId(j,id);
        }
        //std::cout << std::endl;
        newCells->InsertNextCell(newPolyLine);
      }
      newPolyData->SetLines(newCells);
      //newPolyData->Modified();

      std::cout << "Number of new poly data points: " << newPolyData->GetPoints()->GetNumberOfPoints() << std::endl;
      std::cout << "Number of material data points: " << centerLineMaterialIDs.size() << std::endl;

      // Set data to store.
      vtkSmartPointer<vtkIntArray> materialIDs = vtkSmartPointer<vtkIntArray>::New();
      materialIDs->SetName("MaterialIDs");
      materialIDs->SetNumberOfComponents(1);
      //materialIDs->SetNumberOfTuples(1);
      for (auto& id : centerLineMaterialIDs) {
        //std::cout << id << ",";
        materialIDs->InsertNextValue(id);
      }
      std::cout << std::endl;
      newPolyData->GetPointData()->AddArray(materialIDs);
      newPolyData->Modified();

      vtkSmartPointer<vtkXMLPolyDataWriter> writer = vtkSmartPointer<vtkXMLPolyDataWriter>::New();
      writer->SetFileName(materialFileName.c_str());
      writer->SetInputData(newPolyData);
      writer->Update();
      writer->Write();

      /*
      auto retrievedArray = vtkIntArray::SafeDownCast(newPolyData->GetFieldData()->GetArray("MaterialIDs"));
      std::cout << "mat id " << retrievedArray->GetValue(0) << std::endl;
      std::cout << "mat id " << retrievedArray->GetValue(1) << std::endl;
      */

    }

  private:

    std::string clFileName;
    int materialID;
    vtkIdType numCenterLineVerts;
    std::vector<int> centerLineMaterialIDs;
    vtkSmartPointer<vtkPolyData> surface; 
    vtkSmartPointer<vtkPolyData> centerlines;
    vtkSmartPointer<vtkCellLocator> cellLocator;
    vtkSmartPointer<vtkDoubleArray> radiusData;
    vtkSmartPointer<vtkDoubleArray> normalData;
    vtkSmartPointer<vtkDoubleArray> abscissaData;
    vtkSmartPointer<vtkPointSet> pointSet;
};

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

    void AddClEdit(CenterLineEdit clEdit)
    {
      clEdit_ = clEdit;
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
      } else if (key == "w") {
        clEdit_.write_centerline();
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

        if (startPlane == nullptr) {
          startPlane = vtkSmartPointer<vtkPlaneSource>::New();
          vtkSmartPointer<vtkPolyDataMapper> pmapper = vtkSmartPointer<vtkPolyDataMapper>::New();
          pmapper->SetInputConnection(startPlane->GetOutputPort());
          vtkSmartPointer<vtkActor> startPlaneActor = vtkSmartPointer<vtkActor>::New();
          startPlaneActor->SetMapper(pmapper);
          startPlaneActor->GetProperty()->SetColor(1.0, 0.0, 0.0);
          this->GetDefaultRenderer()->AddActor(startPlaneActor);
        }

        double radius = 0.1;
        double inscribedRadius;
        double normal[3], tangent[3], binormal[3], p1[3];
        double planeWidth, origin[3], point1[3], point2[3], vec1[3], vec2[3];
        int index;

        // Get centerline data at the picked point.
        clEdit_.locate_cell(pos, index, inscribedRadius, normal, tangent);

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
    CenterLineEdit clEdit_;
    vtkSmartPointer<vtkLineSource> line; 

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
  std::string surf_file_name = argv[1];
  auto surface = read_poly_data(surf_file_name);
  vtkIdType numSurfVerts = surface->GetNumberOfPoints();
  vtkIdType numPolygons = surface->GetNumberOfPolys();
  std::cout << "Surface: " << std::endl;
  std::cout << "   Number of vertices " << numSurfVerts << std::endl;
  std::cout << "   Number of polygons " << numPolygons << std::endl;
  auto gr_surf = create_graphics_geometry(surface);
  gr_surf->GetProperty()->SetColor(0.8, 0.8, 0.8);
  gr_surf->GetProperty()->SetOpacity(0.5);
  //gr_surf->GetProperty()->SetRepresentationToWireframe();
  //gr_surf->GetProperty()->FrontfaceCullingOn();
  //gr_surf->GetProperty()->BackfaceCullingOn();
  gr_surf->PickableOff();

  // Read and display centerlines.
  //
  std::string cl_file_name = argv[2];
  auto lines = read_poly_data(cl_file_name);
  vtkIdType numLineVerts = lines->GetNumberOfPoints();
  vtkIdType numLines = lines->GetNumberOfLines();
  std::cout << "Lines: " << std::endl;
  std::cout << "   Number of vertices " << numLineVerts << std::endl;
  std::cout << "   Number of lines " << numLines << std::endl;
  // Create lines graphics geometry.
  auto gr_lines = create_graphics_geometry(lines);
  gr_lines->GetProperty()->SetColor(1.0, 0.0, 0.0);
  gr_lines->GetProperty()->SetLineWidth(4.0);

  // Create object to edit centerlines.
  auto clEdit = CenterLineEdit(surface, lines, cl_file_name);

  // Add a renderer.
  vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
  renderer->AddActor(gr_lines);
  renderer->AddActor(gr_surf);
  renderer->SetBackground(1.0, 1.0, 1.0); 

  // Add a render window.
  vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(1600, 1400); 

  // Add window interactor to use trackball and intercept key presses.
  //
  vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  renderWindowInteractor->SetRenderWindow(renderWindow);
  vtkSmartPointer<MouseInteractorStyle> style = vtkSmartPointer<MouseInteractorStyle>::New();
  style->AddClEdit(clEdit);
  renderWindowInteractor->SetInteractorStyle(style);
  style->SetDefaultRenderer(renderer);
  renderWindowInteractor->SetInteractorStyle(style);

  renderWindowInteractor->Initialize();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
