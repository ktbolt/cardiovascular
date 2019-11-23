
#include <string>
//#include <bits/stdc++.h> 

#include <vtkActor.h>
#include <vtkCellData.h>
#include <vtkCell.h>
#include <vtkCellArray.h>
#include <vtkCellData.h>
#include <vtkCellPicker.h>
#include <vtkCellType.h>
#include <vtkGenericCell.h>
#include <vtkGeometryFilter.h>
#include <vtkDataSetMapper.h>
#include <vtkDoubleArray.h>
#include <vtkExtractSelection.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkNamedColors.h>
#include <vtkPolyData.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderer.h>
#include <vtkRendererCollection.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkSelection.h>
#include <vtkSelectionNode.h>
#include <vtkShrinkFilter.h>
#include <vtkSmartPointer.h>
#include <vtkThreshold.h>
#include <vtkTriangleFilter.h>
#include "vtkUnsignedCharArray.h"
#include <vtkUnstructuredGrid.h>
#include <vtkXMLUnstructuredGridReader.h>

#include <vtkDataSetSurfaceFilter.h>
#include <vtkIntArray.h>
#include <vtkCellLocator.h>
#include <vtkPolygon.h>
#include <vtkPointData.h>
#include <vtkAppendFilter.h>
#include <vtkAppendPolyData.h>
#include <vtkCoincidentPoints.h>

#define SV_ERROR 1
#define SV_OK    0

//---------------------- 
// MouseInteractorStyle
//---------------------- 
// This class is used to select cells.
//
class MouseInteractorStyle : public vtkInteractorStyleTrackballCamera
{
public:
  static MouseInteractorStyle* New();

  MouseInteractorStyle()
  {
    selectedMapper = vtkSmartPointer<vtkDataSetMapper>::New();
    selectedActor = vtkSmartPointer<vtkActor>::New();
  }

  virtual void OnKeyPress() override
  //virtual void OnLeftButtonDown() override
  {
    vtkRenderWindowInteractor* rwi = this->Interactor;
    std::string key = rwi->GetKeySym();
    std::cout << "Pressed " << key << std::endl;
      
    if (key != "s") {
        return;
    }

    vtkSmartPointer<vtkNamedColors> colors = vtkSmartPointer<vtkNamedColors>::New();

    // Get the location of the click (in window coordinates)
    int* pos = this->GetInteractor()->GetEventPosition();

    vtkSmartPointer<vtkCellPicker> picker = vtkSmartPointer<vtkCellPicker>::New();
    picker->SetTolerance(0.0005);

    // Pick from this location.
    picker->Pick(pos[0], pos[1], 0, this->GetDefaultRenderer());

    double* worldPosition = picker->GetPickPosition();
    std::cout << "Cell id is: " << picker->GetCellId() << std::endl;

    if (picker->GetCellId() != -1) {
      std::cout << "Pick position is: " << worldPosition[0] << " "
                << worldPosition[1] << " " << worldPosition[2] << endl;
      vtkSmartPointer<vtkIdTypeArray> ids = vtkSmartPointer<vtkIdTypeArray>::New();
      ids->SetNumberOfComponents(1);
      ids->InsertNextValue(picker->GetCellId());

      vtkSmartPointer<vtkSelectionNode> selectionNode = vtkSmartPointer<vtkSelectionNode>::New();
      selectionNode->SetFieldType(vtkSelectionNode::CELL);
      selectionNode->SetContentType(vtkSelectionNode::INDICES);
      selectionNode->SetSelectionList(ids);

      vtkSmartPointer<vtkSelection> selection = vtkSmartPointer<vtkSelection>::New();
      selection->AddNode(selectionNode);

      vtkSmartPointer<vtkExtractSelection> extractSelection = vtkSmartPointer<vtkExtractSelection>::New();
      extractSelection->SetInputData(0, this->Data);
      extractSelection->SetInputData(1, selection);
      extractSelection->Update();

      // In selection
      vtkSmartPointer<vtkUnstructuredGrid> selected = vtkSmartPointer<vtkUnstructuredGrid>::New();
      selected->ShallowCopy(extractSelection->GetOutput());

      std::cout << "There are " << selected->GetNumberOfPoints() << " points in the selection." << std::endl;
      std::cout << "There are " << selected->GetNumberOfCells() << " cells in the selection." << std::endl;
      selectedMapper->SetInputData(selected);
      selectedMapper->ScalarVisibilityOff();
      selectedActor->SetMapper(selectedMapper);
      //selectedActor->GetProperty()->EdgeVisibilityOn();
      selectedActor->GetProperty()->SetRepresentationToWireframe();
      selectedActor->GetProperty()->SetColor(colors->GetColor3d("Green").GetData());
      selectedActor->GetProperty()->SetLineWidth(4);

      this->Interactor->GetRenderWindow()->GetRenderers()->GetFirstRenderer()->AddActor(selectedActor);
    }
    // Forward events
    //vtkInteractorStyleTrackballCamera::OnLeftButtonDown();
  }

  vtkSmartPointer<vtkUnstructuredGrid> Data;
  //vtkSmartPointer<vtkPolyData> Data;
  vtkSmartPointer<vtkDataSetMapper> selectedMapper;
  vtkSmartPointer<vtkActor> selectedActor;
};

vtkStandardNewMacro(MouseInteractorStyle);

//----------
// readMesh
//----------
//
vtkSmartPointer<vtkUnstructuredGrid> 
readMesh(std::string fileName)
{
  std::cout << std::endl;
  std::cout << "=============== Read Mesh =============== " << std::endl;
  std::cout << "file name: " << fileName << std::endl;

  // Read VTK unstructured mesh (.vtu) file.
  //
  vtkSmartPointer<vtkXMLUnstructuredGridReader> reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();
  auto mesh = reader->GetOutput();

  // Convert mesh to polydata.
  /*
  vtkSmartPointer<vtkGeometryFilter> geometryFilter = vtkSmartPointer<vtkGeometryFilter>::New();
  geometryFilter->SetInputData(mesh);
  geometryFilter->Update(); 
  vtkPolyData* meshPolyData = geometryFilter->GetOutput();

  vtkSmartPointer<vtkTriangleFilter> triangleFilter = vtkSmartPointer<vtkTriangleFilter>::New();
  triangleFilter->SetInputData(meshPolyData);
  triangleFilter->Update();
  */

  // Print mesh information.
  //
  vtkIdType numCells = mesh->GetNumberOfCells();
  vtkCellArray* cells = mesh->GetCells();
  vtkUnsignedCharArray* cellTypes = mesh->GetCellTypesArray();

  int numTri = 0;
  int numTet = 0;
  int numHex = 0;
  int numWedge = 0;
  int numQuad = 0;
  int numLine = 0;

  vtkGenericCell* cell = vtkGenericCell::New();
  // Comment out the following line to enable printing to cout.
  std::cout.setstate(std::ios_base::badbit);     

  for (vtkIdType cellId = 0; cellId < numCells; cellId++) {
    mesh->GetCell(cellId, cell);
    auto dim = cell->GetCellDimension();
    auto numPts = cell->GetNumberOfPoints();
    std::cout << "cell " << cellId << "  dim " << dim;
    std::cout << "  numPts " << numPts;
    std::cout << "  topo";
    switch (cellTypes->GetValue(cellId)) {
      case VTK_TETRA:
        std::cout << " tet ";
        numTet += 1;
      break;
      case VTK_HEXAHEDRON:
        std::cout << " hex ";
        numHex += 1;
      break;
      case VTK_WEDGE:
        std::cout << " wedge ";
        numWedge += 1;
      break;
      case VTK_TRIANGLE:
        std::cout << " tri ";
        numTri++;
      break;
      case VTK_QUAD:
        std::cout << " quad ";
        numQuad += 1;
      break;
      case VTK_VERTEX:
        std::cout << " vert ";
      break;
      case VTK_LINE:
        std::cout << " line ";
        numLine += 1;
      break;
      default:
          std::cout << " *** unknown *** '" << cellTypes->GetValue(cellId) << "'";
      break;
    }

    std::cout << "  conn: ";
    for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
      auto id = cell->PointIds->GetId(pointInd);
      std::cout << id << " ";
    }
    std::cout << std::endl;
  }

  std::cout.clear();
  std::cout << std::endl;
  std::cout << "  Number of points: " << mesh->GetNumberOfPoints() << std::endl; 
  std::cout << "  Number of cells " << numCells << std::endl;
  std::cout << "  Number of hex cells " << numHex << std::endl;
  std::cout << "  Number of tet cells " << numTet << std::endl;
  std::cout << "  Number of wedge cells " << numWedge << std::endl;
  std::cout << "  Number of tri cells " << numTri << std::endl;
  std::cout << "  Number of quad cells " << numQuad << std::endl;
  std::cout << "  Number of line cells " << numLine << std::endl;

  return mesh;
}

//------------
// shrinkMesh
//------------
//
vtkSmartPointer<vtkUnstructuredGrid> 
shrinkMesh(vtkSmartPointer<vtkUnstructuredGrid> mesh)
{
  auto shrinkFactor = 0.9;
  vtkSmartPointer<vtkShrinkFilter> shrinkFilter = vtkSmartPointer<vtkShrinkFilter>::New();
  shrinkFilter->SetInputData(mesh);
  shrinkFilter->SetShrinkFactor(shrinkFactor);
  shrinkFilter->Update();
  return shrinkFilter->GetOutput();
}

//-------------
// addGeometry
//-------------
//
vtkSmartPointer<vtkActor> 
addGeometry(vtkSmartPointer<vtkUnstructuredGrid> mesh)
{
  vtkSmartPointer<vtkDataSetMapper> mapper = vtkSmartPointer<vtkDataSetMapper>::New();
  mapper->SetInputData(mesh);

  vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
  mapper->ScalarVisibilityOff();
  actor->SetMapper(mapper);
  actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
  //actor->GetProperty()->SetRepresentationToWireframe();
  //actor->GetProperty()->EdgeVisibilityOn();
  actor->GetProperty()->BackfaceCullingOn();
  return actor;
}

int VtkUtils_PDCheckArrayName(vtkPolyData *object,int datatype,std::string arrayname )
{
  vtkIdType i;
  int numArrays;
  int exists =0;

  if (datatype == 0)
  {
    numArrays = object->GetPointData()->GetNumberOfArrays();
    for (i=0;i<numArrays;i++)
    {
      if (!strcmp(object->GetPointData()->GetArrayName(i),arrayname.c_str()))
      {
        exists =1;
      }
    }
  }
  else
  {
    numArrays = object->GetCellData()->GetNumberOfArrays();
    for (i=0;i<numArrays;i++)
    {
      if (!strcmp(object->GetCellData()->GetArrayName(i),arrayname.c_str()))
      {
        exists =1;
      }
    }
  }

  if (exists == 1)
  {
    return SV_OK;
  }
  else
  {
    return SV_ERROR;
  }
}


int VMTKUtils_ResetOriginalRegions(vtkPolyData *newgeom,
    vtkPolyData *originalgeom,
    std::string regionName,
    vtkIdList *onlyList,
    int dummy)
{
  int i,j,k;
  int subId;
  int region;
  int temp;
  int flag = 1;
  int count;
  int bigcount;
  vtkIdType npts;
  vtkIdType *pts;
  double distance;
  double closestPt[3];
  double tolerance = 1.0;
  double centroid[3];
  int range;
  vtkIdType closestCell;
  vtkIdType cellId;
  vtkIdType currentValue;
  vtkIdType realValue;
  vtkSmartPointer<vtkCellLocator> locator =
    vtkSmartPointer<vtkCellLocator>::New();
  vtkSmartPointer<vtkGenericCell> genericCell =
    vtkSmartPointer<vtkGenericCell>::New();
  vtkSmartPointer<vtkPolyData> originalCopy =
    vtkSmartPointer<vtkPolyData>::New();

  if (onlyList == NULL)
  {
    fprintf(stderr,"Cannot give NULL onlyList. Use other reset function without only list\n");
    return SV_ERROR;
  }

  newgeom->BuildLinks();
  originalgeom->BuildLinks();
  originalCopy->DeepCopy(originalgeom);

  if (VtkUtils_PDCheckArrayName(originalCopy,1, regionName) != SV_OK)
  {
    fprintf(stderr,"Array name %s does not exist. Regions must be identified \
		    and named 'ModelFaceID' prior to this function call\n",  regionName.c_str());
    return SV_ERROR;
  }

  vtkDataArray *testRegions = originalCopy->GetCellData()->GetScalars( regionName.c_str());

  if (VtkUtils_PDCheckArrayName(newgeom,1, regionName.c_str()) != SV_OK)
  {
    fprintf(stderr,"Array name %s does not exist. Regions must be identified \
        and named 'ModelFaceID' prior to this function call\n", regionName.c_str());
    return SV_ERROR;
  }

  vtkDataArray *currentRegions = newgeom->GetCellData()->GetArray(regionName.c_str());

  locator->SetDataSet(originalCopy);
  locator->BuildLocator();
  vtkDataArray *realRegions = originalCopy->GetCellData()->GetScalars( regionName.c_str());

  for (cellId=0;cellId<newgeom->GetNumberOfCells();cellId++)
  {
    currentValue = currentRegions->GetTuple1(cellId);
    if (onlyList->IsId(currentValue) == -1)
    {
      continue;
    }

    newgeom->GetCellPoints(cellId,npts,pts);
    vtkSmartPointer<vtkPoints> polyPts = vtkSmartPointer<vtkPoints>::New();
    vtkSmartPointer<vtkIdTypeArray> polyPtIds = vtkSmartPointer<vtkIdTypeArray>::New();
    for (i=0;i<npts;i++)
    {
      polyPtIds->InsertValue(i,i);
      polyPts->InsertNextPoint(newgeom->GetPoint(pts[i]));
    }
    vtkPolygon::ComputeCentroid(polyPtIds,polyPts,centroid);

    locator->FindClosestPoint(centroid,closestPt,genericCell,closestCell,
	subId,distance);
    currentRegions->SetTuple1(cellId,realRegions->GetTuple1(closestCell));
  }

  newgeom->GetCellData()->SetActiveScalars(regionName.c_str());

  return SV_OK;
}



int VMTKUtils_ResetOriginalRegions(vtkPolyData *newgeom, vtkPolyData *originalgeom, std::string regionName)
{
  int i,j,k;
  int subId;
  int maxIndex;
  int temp;
  int flag = 1;
  int count;
  int bigcount;
  vtkIdType npts;
  vtkIdType *pts;
  double distance;
  double closestPt[3];
  double tolerance = 1.0;
  double centroid[3];
  int range;
  vtkIdType closestCell;
  vtkIdType cellId;
  vtkIdType currentValue;
  vtkIdType realValue;
  vtkSmartPointer<vtkCellLocator> locator =
    vtkSmartPointer<vtkCellLocator>::New();
  vtkSmartPointer<vtkGenericCell> genericCell =
    vtkSmartPointer<vtkGenericCell>::New();
  vtkSmartPointer<vtkIntArray> currentRegions =
    vtkSmartPointer<vtkIntArray>::New();
  vtkSmartPointer<vtkIntArray> realRegions =
    vtkSmartPointer<vtkIntArray>::New();

  newgeom->BuildLinks();
  originalgeom->BuildLinks();
  locator->SetDataSet(originalgeom);
  locator->BuildLocator();

  if (VtkUtils_PDCheckArrayName(originalgeom,1,regionName) != SV_OK)
  {
    fprintf(stderr,"Array name 'ModelFaceID' does not exist. Regions must be identified \
		    and named 'ModelFaceID' prior to this function call\n");
    return SV_ERROR;
  }

  realRegions = static_cast<vtkIntArray*>(originalgeom->GetCellData()->GetScalars(regionName.c_str()));


  for (cellId=0;cellId<newgeom->GetNumberOfCells();cellId++)
  {
      newgeom->GetCellPoints(cellId,npts,pts);
      //int eachValue[npts];
      vtkSmartPointer<vtkPoints> polyPts = vtkSmartPointer<vtkPoints>::New();
      vtkSmartPointer<vtkIdTypeArray> polyPtIds = vtkSmartPointer<vtkIdTypeArray>::New();
      for (i=0;i<npts;i++)
      {
	polyPtIds->InsertValue(i,i);
	polyPts->InsertNextPoint(newgeom->GetPoint(pts[i]));
      }
      vtkPolygon::ComputeCentroid(polyPtIds,polyPts,centroid);

      locator->FindClosestPoint(centroid,closestPt,genericCell,closestCell,
	  subId,distance);
      currentRegions->InsertValue(cellId,realRegions->GetValue(closestCell));
  }

  newgeom->GetCellData()->RemoveArray(regionName.c_str());
  currentRegions->SetName(regionName.c_str());
  newgeom->GetCellData()->AddArray(currentRegions);

  newgeom->GetCellData()->SetActiveScalars(regionName.c_str());

  return SV_OK;
}

//---------------
// processMeshes
//---------------
//
int
processMeshes(vtkSmartPointer<vtkUnstructuredGrid> meshFromTetGen, vtkSmartPointer<vtkUnstructuredGrid> boundaryMesh,
  vtkSmartPointer<vtkUnstructuredGrid> surfaceWithSize, int newRegionBoundaryLayer)
{
  std::cout << std::endl;
  std::cout << "=============== Process Meshes =============== " << std::endl;

  // Get model regions on tetgen mesh
  vtkDataArray *meshFromTetGenRegionIds = meshFromTetGen->GetCellData()->GetArray("ModelRegionID");
  if (meshFromTetGenRegionIds == NULL)
  {
    fprintf(stderr,"No model region id on tetgen mesh\n");
    return SV_ERROR;
  }

  // TODO: Will need to change if same region not on all exterior of mesh
  double minmax[2];
  meshFromTetGenRegionIds->GetRange(minmax);
  if (minmax[0] != minmax[1])
  {
    fprintf(stderr,"Cannot currently handle multi-domains on surface of tetgen mesh");
    return SV_ERROR;
  }
  int modelId = minmax[0];

  // Add model region id to surface
  vtkSmartPointer<vtkIntArray> surfaceRegionIds =
    vtkSmartPointer<vtkIntArray>::New();
  surfaceRegionIds->SetNumberOfComponents(1);
  surfaceRegionIds->SetNumberOfTuples(surfaceWithSize->GetNumberOfCells());
  surfaceRegionIds->FillComponent(0, modelId);
  surfaceRegionIds->SetName("ModelRegionID");
  surfaceWithSize->GetCellData()->AddArray(surfaceRegionIds);

  if (newRegionBoundaryLayer)
  {
    modelId++;
  }

  // Add model region id to boundary layer
  vtkSmartPointer<vtkIntArray> boundaryMeshRegionIds =
    vtkSmartPointer<vtkIntArray>::New();
  boundaryMeshRegionIds->SetNumberOfComponents(1);
  boundaryMeshRegionIds->SetNumberOfTuples(boundaryMesh->GetNumberOfCells());
  boundaryMeshRegionIds->FillComponent(0, modelId);
  boundaryMeshRegionIds->SetName("ModelRegionID");
  boundaryMesh->GetCellData()->AddArray(boundaryMeshRegionIds);

  // Separate the surface and volume cells from the boundary layer mesh
  vtkSmartPointer<vtkIntArray> isSurface =
    vtkSmartPointer<vtkIntArray>::New();
  isSurface->SetNumberOfComponents(1);
  isSurface->SetNumberOfTuples(boundaryMesh->GetNumberOfCells());
  isSurface->SetName("isSurface");

  for (int i=0;i<boundaryMesh->GetNumberOfCells();i++) {
    if (boundaryMesh->GetCellType(i) == VTK_TRIANGLE || boundaryMesh->GetCellType(i) == VTK_QUAD) {
      isSurface->SetTuple1(i,1);
    } else {
      isSurface->SetTuple1(i,0);
    }
  }
  boundaryMesh->GetCellData()->AddArray(isSurface);

  // Threshold out the surface
  vtkSmartPointer<vtkThreshold> thresholder =
    vtkSmartPointer<vtkThreshold>::New();
  thresholder->SetInputData(boundaryMesh);
  thresholder->SetInputArrayToProcess(0,0,0,1,"isSurface");
  thresholder->ThresholdBetween(1,1);
  thresholder->Update();

  vtkSmartPointer<vtkDataSetSurfaceFilter> surfacer =
    vtkSmartPointer<vtkDataSetSurfaceFilter>::New();
  surfacer->SetInputData(thresholder->GetOutput());
  surfacer->Update();

  vtkSmartPointer<vtkPolyData> boundaryMeshSurface =
    vtkSmartPointer<vtkPolyData>::New();
  boundaryMeshSurface->DeepCopy(surfacer->GetOutput());

  // Threshold out the volume
  thresholder->SetInputData(boundaryMesh);
  thresholder->SetInputArrayToProcess(0,0,0,1,"isSurface");
  thresholder->ThresholdBetween(0,0);
  thresholder->Update();
  vtkSmartPointer<vtkUnstructuredGrid> boundaryMeshVolume = vtkSmartPointer<vtkUnstructuredGrid>::New();
  boundaryMeshVolume->DeepCopy(thresholder->GetOutput());

  // Add the model face id back to the cap region that doesn't have it on surface bl
  thresholder->SetInputData(surfaceWithSize);
  thresholder->SetInputArrayToProcess(0,0,0,1,"WallID");
  thresholder->ThresholdBetween(0,0);
  thresholder->Update();

  surfacer->SetInputData(thresholder->GetOutput());
  surfacer->Update();

  vtkSmartPointer<vtkPolyData> surfaceMeshCaps =
    vtkSmartPointer<vtkPolyData>::New();
  surfaceMeshCaps->DeepCopy(surfacer->GetOutput());

  vtkDataArray *cellEntityIds = boundaryMeshSurface->GetCellData()->GetArray("CellEntityIds");
  int entityId;
  for (int i=0; i<boundaryMeshSurface->GetNumberOfCells(); i++) {
    entityId = cellEntityIds->GetTuple1(i);
    if (entityId == 9999) {
      boundaryMeshSurface->GetCellData()->GetArray("ModelFaceID")->SetTuple1(i, 9999);
    }
  }

  vtkSmartPointer<vtkIdList> onlyList = vtkSmartPointer<vtkIdList>::New();
  onlyList->InsertNextId(9999);
  if (VMTKUtils_ResetOriginalRegions(boundaryMeshSurface, surfaceMeshCaps, "ModelFaceID", onlyList, 1) != SV_OK)
  {
    fprintf(stderr,"Failure in resetting model face id on boundary layer caps\n");
    return SV_ERROR;
  }

  vtkSmartPointer<vtkUnstructuredGrid> newMeshVolume = vtkSmartPointer<vtkUnstructuredGrid>::New();
  vtkSmartPointer<vtkPolyData> newMeshSurface = vtkSmartPointer<vtkPolyData>::New();

  if (newRegionBoundaryLayer) {

    // Create points hash table.
    //
    std::cout << "Create unique IDs. " << std::endl; 
    vtkSmartPointer<vtkCoincidentPoints> pointsHash = vtkSmartPointer<vtkCoincidentPoints>::New();
    auto numVolPoints = meshFromTetGen->GetNumberOfPoints();
    auto volPoints = meshFromTetGen->GetPoints();
    int nodeID = 1;
    for (int i = 0; i < numVolPoints; i++) {
      double pt[3];
      volPoints->GetPoint(i,pt);
      pointsHash->AddPoint(nodeID, pt);
      nodeID += 1;
    }
    auto boundPoints = boundaryMeshVolume->GetPoints();
    for (int i = 0; i < boundaryMeshVolume->GetNumberOfPoints(); i++) {
      double pt[3];
      int id;
      boundPoints->GetPoint(i,pt);
      pointsHash->AddPoint(nodeID, pt);
      nodeID += 1;
    }

    // Add global node IDs to interior mesh.
    //
    // IDs range from 1 to meshFromTetGen->GetNumberOfPoints().
    //
    std::cout << "Add node IDs to meshFromTetGen. " << std::endl; 
    std::cout << "  Number of points: " << meshFromTetGen->GetNumberOfPoints() << std::endl; 
    vtkSmartPointer<vtkIntArray> globalNodeIds0 = vtkSmartPointer<vtkIntArray>::New();
    globalNodeIds0->SetNumberOfTuples(meshFromTetGen->GetNumberOfPoints());
    globalNodeIds0->SetName("GlobalNodeID");
    int globalNodeID = 1;
    for (int i = 0; i < meshFromTetGen->GetNumberOfPoints(); i++) {
      globalNodeIds0->SetTuple1(i,globalNodeID);
      globalNodeID++;
    }
    std::cout << "  globalNodeID: " << globalNodeID<< std::endl; 
    meshFromTetGen->GetPointData()->AddArray(globalNodeIds0);

    // Add global node IDs to boundary mesh.
    //
    // There are duplicate nodes on the interior/boundary layer interface
    // so we use the node IDs from the meshFromTetGen.
    //
    std::cout << "Add node IDs to boundaryMeshVolume. " << std::endl; 
    std::cout << "  Number of points: " << boundaryMeshVolume->GetNumberOfPoints() << std::endl; 
    vtkSmartPointer<vtkIntArray> globalNodeIds1 = vtkSmartPointer<vtkIntArray>::New();
    globalNodeIds1->SetNumberOfTuples(boundaryMeshVolume->GetNumberOfPoints());
    globalNodeIds1->SetName("GlobalNodeID");
    int numNewNodes = 0;
    int numDupeNodes = 0;

    //for (int i = 0; i < 6; i++) {
    for (int i = 0; i < boundaryMeshVolume->GetNumberOfPoints(); i++) {
      double pt[3];
      int id; 
      boundPoints->GetPoint(i,pt);
      //std::cout << "  boundary node: " << i << " " << pt[0] << " " << pt[1] << "  " << pt[2] << std::endl; 
      auto ids = pointsHash->GetCoincidentPointIds(pt);
      if (ids == nullptr) {
        //std::cout << "  ids is null " << std::endl; 
        id = globalNodeID;
        globalNodeID += 1;
        numNewNodes += 1;
      } else {
        int n = ids->GetNumberOfIds();
        auto id = ids->GetId(0);
        auto id1 = ids->GetId(0);
        auto id2 = ids->GetId(1);
        numDupeNodes += 1;
        std::cout << "  Dupe node at: n:" << n << "  i:" << i << "  use: " << id << std::endl; 
        std::cout << "    id1: " << id1 << " " << "  id2: " << id2 << std::endl; 
      }
      globalNodeIds1->SetTuple1(i,id);
    }
    std::cout << "  globalNodeID: " << globalNodeID << std::endl; 
    std::cout << "  numNewNodes: " << numNewNodes << std::endl; 
    std::cout << "  numNewNodes: " << numNewNodes << std::endl; 
    boundaryMeshVolume->GetPointData()->AddArray(globalNodeIds1);

    // Add element IDs to interior mesh.
    vtkSmartPointer<vtkIntArray> globalElementIds0 = vtkSmartPointer<vtkIntArray>::New();
    globalElementIds0->SetNumberOfTuples(meshFromTetGen->GetNumberOfCells());
    globalElementIds0->SetName("GlobalElementID");
    int globalElemID = 1;
    for (int i=0;i<meshFromTetGen->GetNumberOfCells();i++) {
      globalElementIds0->SetTuple1(i,globalElemID);
      globalElemID++;
    }
    meshFromTetGen->GetCellData()->AddArray(globalElementIds0);

    // Add global element IDs to boundary mesh.
    vtkSmartPointer<vtkIntArray> globalElementIds1 = vtkSmartPointer<vtkIntArray>::New();
    globalElementIds1->SetNumberOfTuples(boundaryMeshVolume->GetNumberOfCells());
    globalElementIds1->SetName("GlobalElementID");
    for (int i = 0; i < boundaryMeshVolume->GetNumberOfCells(); i++) {
      globalElementIds1->SetTuple1(i,globalElemID);
      globalElemID++;
    }
    boundaryMeshVolume->GetCellData()->AddArray(globalElementIds1);

    // Extract surface of boundary layer mesh.
    surfacer->SetInputData(boundaryMeshVolume);
    surfacer->Update();
    vtkSmartPointer<vtkPolyData> surface0 = vtkSmartPointer<vtkPolyData>::New();
    surface0->DeepCopy(surfacer->GetOutput());

    if (VMTKUtils_ResetOriginalRegions(surface0, boundaryMeshSurface, "ModelFaceID") != SV_OK) {
      fprintf(stderr,"Failure in resetting model face id on final mesh surface\n");
      return SV_ERROR;
    }

    // Extract surface of interior mesh.
    surfacer->SetInputData(meshFromTetGen);
    surfacer->Update();
    vtkSmartPointer<vtkPolyData> surface1 = vtkSmartPointer<vtkPolyData>::New();
    surface1->DeepCopy(surfacer->GetOutput());
    surfacer->SetInputData(surfaceWithSize);
    surfacer->Update();

    if (VMTKUtils_ResetOriginalRegions(surface1, surfacer->GetOutput(), "ModelFaceID") != SV_OK) {
      fprintf(stderr,"Failure in resetting model face id on final mesh surface\n");
      return SV_ERROR;
    }

    // Combine boundary and interior surfaces.
    vtkSmartPointer<vtkAppendPolyData> boundaryAppender = vtkSmartPointer<vtkAppendPolyData>::New();
    boundaryAppender->AddInputData(surface0);
    boundaryAppender->AddInputData(surface1);
    boundaryAppender->Update();
    newMeshSurface->DeepCopy(boundaryAppender->GetOutput());

    // Combine boundary and interior volume meshes. 
    vtkSmartPointer<vtkAppendFilter> appender = vtkSmartPointer<vtkAppendFilter>::New();
    appender->AddInputData(boundaryMeshVolume);
    appender->AddInputData(meshFromTetGen);
    appender->SetMergePoints(true);
    appender->Update();
    newMeshVolume->DeepCopy(appender->GetOutput());
    auto nodeIDs = vtkIntArray::SafeDownCast(newMeshVolume->GetPointData()->GetArray("GlobalNodeID"));

    std::cout << "New volume mesh. " << std::endl; 
    std::cout << "  Number of points: " << newMeshVolume->GetNumberOfPoints() << std::endl; 
    std::cout << "  Number of node IDs: " << nodeIDs->GetNumberOfTuples() << std::endl; 
    std::vector<int> ids;
    for (int i = 0; i < nodeIDs->GetNumberOfTuples(); i++) {
      auto id = nodeIDs->GetValue(i);
      ids.push_back(id);
    }
    std::sort(ids.begin(), ids.end());
    std::cout << "    ID range: " << ids[0] << ", " << ids.back() << std::endl;

/*
    int numDupeB = 0;
    double pt1[3], pt2[3];
    for (int i = 0; i < numVolPoints; i++) {
      volPoints->GetPoint(i,pt1);
      for (int j = 0; j < boundaryMeshVolume->GetNumberOfPoints(); j++) {
        boundPoints->GetPoint(j,pt2);
        auto dx = pt1[0] - pt2[0];
        auto dy = pt1[1] - pt2[1];
        auto dz = pt1[2] - pt2[2];
        auto d = sqrt(dx*dx + dy*dy + dz*dz);
        if (d < 1e-6) {
          std::cout << "  Duplicate: vol " << i << "  with bound " << j << std::endl; 
          std::cout << "  volume node: " << i << " " << pt1[0] << " " << pt1[1] << "  " << pt1[2] << std::endl; 
          numDupeB += 1;
          break;
        }
      }
      if (numDupeB == 1) {
        break;
      }
    }
    std::cout << "  Num b duplicate: " << numDupeB << std::endl; 
*/
  }


}

//------
// main
//------

int main(int argc, char* argv[])
{
  vtkObject::GlobalWarningDisplayOff();
  auto tetgenMesh = readMesh("meshFromTetGen.vtu");
  auto tetgenMeshShrink = shrinkMesh(tetgenMesh);
  auto tetgenMeshActor = addGeometry(tetgenMeshShrink);
  tetgenMeshActor->GetProperty()->SetColor(1.0, 0.0, 0.0);

  auto boundaryMesh = readMesh("boundaryMesh.vtu");
  auto boundaryMeshShrink = shrinkMesh(boundaryMesh);
  auto boundaryMeshActor = addGeometry(boundaryMeshShrink);
  boundaryMeshActor->GetProperty()->SetColor(0.0, 1.0, 0.0);

  auto surfaceWithSize = readMesh("surfaceWithSize.vtu");

  // Create renderer.
  vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
  renderer->AddActor(tetgenMeshActor);
  renderer->AddActor(boundaryMeshActor);
  renderer->SetBackground(1.0, 1.0, 1.0); 

  // Process meshes.
  int newRegionBoundaryLayer = 1;
  processMeshes(tetgenMesh, boundaryMesh, surfaceWithSize, newRegionBoundaryLayer);

  // Create render window.
  vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(500, 500);

  // Add window interactor.
  vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  renderWindowInteractor->SetRenderWindow(renderWindow);

  // Cell picking interactor.
  vtkSmartPointer<MouseInteractorStyle> style = vtkSmartPointer<MouseInteractorStyle>::New();
  style->SetDefaultRenderer(renderer);
  style->Data = tetgenMesh;

  renderWindowInteractor->SetInteractorStyle(style);
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
