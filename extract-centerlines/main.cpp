//
// This program is use to extract centerlines from a polygonal surface
//
#include <string>

#include <vtkvmtkCapPolyData.h>
#include <vtkvmtkSimpleCapPolyData.h>
#include <vtkvmtkPolyDataCenterlines.h>

#include <vtkActor.h>
#include <vtkArrowSource.h>
#include <vtkCallbackCommand.h>
#include <vtkCellData.h>
#include <vtkCellLocator.h>
#include <vtkCleanPolyData.h>
#include <vtkCommand.h>
#include <vtkDataSetMapper.h>
#include <vtkDoubleArray.h>
#include <vtkFloatArray.h>
#include <vtkGenericCell.h>
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
#include <vtkTriangleFilter.h>
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

#define vtkNew(type,name) \
  vtkSmartPointer<type> name = vtkSmartPointer<type>::New()

//---------------
// DeleteRegions
//---------------
// Remove cells from polydata with given IDs. 
//
bool DeleteRegions(vtkSmartPointer<vtkPolyData> inpd, std::vector<int> regionIDs)
{
    auto msg = "[sv4guiModelUtils::DeleteRegions]";
    std::cout << msg << "---------- DeleteRegions ----------" << std::endl;
    std::cout << msg << "Number of region IDs: " << regionIDs.size() << std::endl;

    if (inpd==NULL) {
        return false;
    }

    std::string arrayname = "ModelFaceID";
    bool existing = false;

    if (inpd->GetCellData()->HasArray(arrayname.c_str())) {
        existing = true;
    }

    if (!existing) {
        return false;
    }
    int numDelCells = 0;

    for (int i = 0; i < regionIDs.size(); i++) {
        vtkSmartPointer<vtkIntArray> boundaryRegions = vtkSmartPointer<vtkIntArray>::New();
        boundaryRegions = vtkIntArray::SafeDownCast(inpd->GetCellData()->GetScalars("ModelFaceID"));
        inpd->BuildLinks();

        for (vtkIdType cellId = 0; cellId < inpd->GetNumberOfCells(); cellId++) {
            if (boundaryRegions->GetValue(cellId) == regionIDs[i]) {
                inpd->DeleteCell(cellId);
                //std::cout << msg << "Delete cellId: " << cellId << std::endl;
                numDelCells += 1;
            }
        }

        inpd->RemoveDeletedCells();
    }

    std::cout << msg << "Number of deleted cells: " << numDelCells << std::endl;

    return true;
}

//--------------
// sys_geom_cap
//--------------
// Add caps to surface geometry.
//
vtkSmartPointer<vtkPolyData> 
sys_geom_cap( vtkSmartPointer<vtkPolyData> geom, int *numcenterids,int **centerids, int type)
{
  auto msg = "[sys_geom_cap] ";
  std::cout << msg << "---------- sys_geom_cap ----------" << std::endl;
  vtkSmartPointer<vtkIdList> capCenterIds = vtkSmartPointer<vtkIdList>::New();
  vtkSmartPointer<vtkTriangleFilter> triangulate = vtkSmartPointer<vtkTriangleFilter>::New();
  int numids;
  int *allids;
  int i;
  vtkSmartPointer<vtkPolyData> result;

  try {

      if (type ==0) {
          vtkSmartPointer<vtkvmtkSimpleCapPolyData> capper = vtkSmartPointer<vtkvmtkSimpleCapPolyData>::New();
          capper->SetInputData(geom);
          capper->SetCellEntityIdsArrayName("CenterlineCapID");
          capper->SetCellEntityIdOffset(1);
          capper->Update();
          triangulate->SetInputData(capper->GetOutput());
          triangulate->Update();
          result = triangulate->GetOutput();
          capCenterIds->InsertNextId(0);

      } else if (type == 1) {
          vtkSmartPointer<vtkvmtkCapPolyData> capper = vtkSmartPointer<vtkvmtkCapPolyData>::New();
          capper->SetInputData(geom);
          capper->SetDisplacement(0);
          capper->SetInPlaneDisplacement(0);
          capper->Update();
          triangulate->SetInputData(capper->GetOutput());
          triangulate->Update();
          result = triangulate->GetOutput();
          capCenterIds->DeepCopy(capper->GetCapCenterIds());
      }

  } catch (...) {
      fprintf(stderr,"ERROR in capping operation.\n");
      fflush(stderr);
      return nullptr;
  }

  numids = capCenterIds->GetNumberOfIds();
  allids = new int[numids];

  for (i=0;i<numids;i++) {
      allids[i] = capCenterIds->GetId(i);
  }

  *numcenterids = numids;
  *centerids = allids;
  std::cout << msg << "numids: " << numids << std::endl;

  return result;
}


//----------------
// sys_geom_Clean
//----------------
// Merge duplicate points, and/or remove unused points and/or remove degenerate cells.
//
vtkSmartPointer<vtkPolyData> 
sys_geom_Clean( vtkSmartPointer<vtkPolyData> srcPd )
{
  vtkNew(vtkCleanPolyData, cleaner);
  cleaner->SetInputData(srcPd);
  cleaner->Update();

  vtkSmartPointer<vtkPolyData> pd;
  pd = vtkPolyData::New();
  pd->DeepCopy(cleaner->GetOutput());

  return pd;
}

//----------------------
// sys_geom_centerlines
//----------------------
//
vtkSmartPointer<vtkPolyData>
sys_geom_centerlines( vtkSmartPointer<vtkPolyData> surface, int *sources, int nsources, int *targets,int ntargets,
   vtkPolyData **voronoi)
{
  auto msg = "[sys_geom_centerlines] ";
  std::cout << msg << "---------- sys_geom_centerlines ----------" << std::endl;

  vtkSmartPointer<vtkIdList> capInletIds = vtkSmartPointer<vtkIdList>::New();
  vtkSmartPointer<vtkIdList> capOutletIds = vtkSmartPointer<vtkIdList>::New();
  int pointId;

  for (pointId = 0; pointId < nsources; pointId++) {
    capInletIds->InsertNextId(*sources+pointId);
  }
  for (pointId = 0; pointId < ntargets; pointId++) {
    capOutletIds->InsertNextId(*targets+pointId);
  }

  vtkNew(vtkvmtkPolyDataCenterlines, centerLiner);
  vtkSmartPointer<vtkPolyData> centerlines;

  try {
      centerLiner->SetInputData(surface);
      centerLiner->SetSourceSeedIds(capInletIds);
      centerLiner->SetTargetSeedIds(capOutletIds);
      centerLiner->SetRadiusArrayName("MaximumInscribedSphereRadius");
      centerLiner->SetCostFunction("1/R");
      centerLiner->SetFlipNormals(0);
      centerLiner->SetAppendEndPointsToCenterlines(1);
      centerLiner->SetSimplifyVoronoi(0);
      centerLiner->SetCenterlineResampling(0);
      centerLiner->SetResamplingStepLength(1);
      centerLiner->Update();
      centerlines = centerLiner->GetOutput();
      *voronoi = centerLiner->GetVoronoiDiagram();

  } catch (...) {
    fprintf(stderr,"ERROR in centerline operation.\n");
    fflush(stderr);
    return nullptr;
  }

  return centerlines;
}

//----------------------
// CalculateCenterlines
//----------------------
//
vtkSmartPointer<vtkPolyData>
CalculateCenterlines(vtkSmartPointer<vtkPolyData> surface, vtkIdList* sourcePtIds, vtkIdList* targetPtIds)
{
    auto msg = "[CalculateCenterlines] ";
    std::cout << msg << "---------- CalculateCenterlines ----------" << std::endl;
    int numSourcePts = sourcePtIds->GetNumberOfIds();
    std::cout << msg << "numSourcePts: " << numSourcePts << std::endl;
    int *sources = new int[numSourcePts];
    for (int i = 0; i < numSourcePts; i++) {
        sources[i] = sourcePtIds->GetId(i);
    }

    int numTargetPts = targetPtIds->GetNumberOfIds();
    std::cout << msg << "numTargetPts: " << numTargetPts << std::endl;
    int *targets = new int[numTargetPts];
    for (int i = 0; i < numTargetPts; i++) {
        targets[i] = targetPtIds->GetId(i);
    }

    vtkPolyData *voronoi;

    auto centerlines = sys_geom_centerlines(surface, sources, numSourcePts, targets, numTargetPts, &voronoi);

    return centerlines;
}

//-------------------------
// CreateCenterlines_nocap
//-------------------------

vtkSmartPointer<vtkPolyData> 
CreateCenterlines_nocap(vtkSmartPointer<vtkPolyData> surface, vtkIdList *sourceCapIds, std::vector<int>& capFaceIDs,
    std::vector<std::array<double,3>>& capPts)
{
    auto msg = "[CreateCenterlines_nocap] ";
    std::cout << msg << "---------- CreateCenterlines_nocap ----------" << std::endl;
    std::cout << msg << "Number of sourceCapIds: " << sourceCapIds->GetNumberOfIds() << std::endl;

    vtkSmartPointer<vtkPolyData> mesh = vtkSmartPointer<vtkPolyData>::New();
    mesh->DeepCopy(surface);
    mesh->BuildLinks();
    //mesh = sys_geom_Clean(mesh);

    std::cout << msg << "Mesh number of points: " << mesh->GetNumberOfPoints() << std::endl;
    std::vector<std::array<double,3>> cellCenters;
    std::vector<int> capCenterIDs;

    for (int i = 0; i < capFaceIDs.size(); i++) {
        auto faceID = capFaceIDs[i];
        std::cout << msg << "Face id: " << faceID << std::endl;
        vtkSmartPointer<vtkIntArray> boundaryRegions = vtkSmartPointer<vtkIntArray>::New();
        boundaryRegions = vtkIntArray::SafeDownCast(mesh->GetCellData()->GetScalars("ModelFaceID"));
        //mesh->BuildLinks();
        double pt[3];
        double cpt[3] = {0.0, 0.0, 0.0};
        int numCellPts = 0;
        std::vector<int> cellPtIDs; 
        std::vector<std::array<double,3>> cellPts;

        for (vtkIdType cellId = 0; cellId < mesh->GetNumberOfCells(); cellId++) {
            if (boundaryRegions->GetValue(cellId) == faceID) {
                //std::cout << msg << "cellId: " << cellId << std::endl;
                vtkSmartPointer<vtkIdList> pointIdList = vtkSmartPointer<vtkIdList>::New();
                mesh->GetCellPoints(cellId, pointIdList);
                int numPts = pointIdList->GetNumberOfIds();
                for (int j = 0; j < numPts; j++) {
                    auto pid = pointIdList->GetId(j);
                    cellPtIDs.push_back(pid);
                    //std::cout << pid << " ";
                    mesh->GetPoint(pid, pt);
                    cpt[0] += pt[0]; 
                    cpt[1] += pt[1]; 
                    cpt[2] += pt[2]; 
                    cellPts.push_back(std::array<double,3>{pt[0], pt[1], pt[2]});
                    numCellPts += 1;
                }
                //std::cout << msg << std::endl;
            }
        }

        cpt[0] /= numCellPts;
        cpt[1] /= numCellPts;
        cpt[2] /= numCellPts;
        cellCenters.push_back(std::array<double,3>{cpt[0], cpt[1], cpt[2]});
        int centerID;
        double min_dist = 1e9;

        for (int j = 0; j < cellPts.size(); j++) {
            auto pt = cellPts[j];
            double dist = (pt[0]-cpt[0])*(pt[0]-cpt[0]) + (pt[1]-cpt[1])*(pt[1]-cpt[1]) + (pt[2]-cpt[2])*(pt[2]-cpt[2]);
            if (dist < min_dist) {
                centerID = cellPtIDs[j];
                min_dist = dist; 
            } 
        }
        capCenterIDs.push_back(centerID);
    }

    vtkSmartPointer<vtkIdList> sourcePtIds = vtkSmartPointer<vtkIdList>::New();
    vtkSmartPointer<vtkIdList> targetPtIds = vtkSmartPointer<vtkIdList>::New();

    vtkSmartPointer<vtkCellLocator> locator = vtkSmartPointer<vtkCellLocator>::New();
    locator->SetDataSet(mesh);
    locator->BuildLocator();

    int subId;
    double distance;
    double capPt[3];
    double closestPt[3];
    vtkIdType closestCell;
    vtkSmartPointer<vtkGenericCell> genericCell = vtkSmartPointer<vtkGenericCell>::New();

    for (int i = 0; i < cellCenters.size(); i++) {
        int ptId = capCenterIDs[i];
        //int ptId = capCenterIds[i];
        std::cout << msg << "----- ptID " << ptId << " -----" << std::endl;
        mesh->GetPoint(ptId, capPt);
        //capPt[0] = cellCenters[i][0];
        //capPt[1] = cellCenters[i][1];
        //capPt[2] = cellCenters[i][2];
        locator->FindClosestPoint(capPt, closestPt, genericCell, closestCell, subId, distance);
        int capFaceId = mesh->GetCellData()->GetArray("ModelFaceID")->GetTuple1(closestCell);
        //std::cout << msg << "Cap pt: " << capPt[0] << "  " << capPt[1] << "  " << capPt[2] << std::endl;
        //std::cout << msg << "closestPt: " << closestPt[0] << "  " << closestPt[1] << "  " << closestPt[2] << std::endl;
        //std::cout << msg << "closestCell: " << closestCell << std::endl;
        //std::cout << msg << "subId: " << subId << std::endl;
        capPts.push_back(std::array<double,3>{closestPt[0], closestPt[1], closestPt[2]});
        //ptId = closestCell;

        if (sourceCapIds->IsId(capFaceId) != -1) {
            sourcePtIds->InsertNextId(ptId);
            std::cout << msg << "Add source pt ID: " << ptId << std::endl;
        } else {
            targetPtIds->InsertNextId(ptId);
            std::cout << msg << "Add target pt ID: " << ptId << std::endl;
        }
    }

    auto centerlines = CalculateCenterlines(mesh, sourcePtIds, targetPtIds);
    return centerlines;

    //return mesh;
    //return nullptr;
}

//-------------------
// CreateCenterlines
//-------------------
//
vtkSmartPointer<vtkPolyData> 
CreateCenterlines(vtkSmartPointer<vtkPolyData> surface, vtkIdList *sourceCapIds, std::vector<int>& capFaceIDs,
    std::vector<std::array<double,3>>& capPts)
{
    auto msg = "[CreateCenterlines] ";
    std::cout << msg << "---------- CreateCenterlines ----------" << std::endl;
    std::cout << msg << "Number of sourceCapIds: " << sourceCapIds->GetNumberOfIds() << std::endl;

    vtkSmartPointer<vtkPolyData> inpd = vtkSmartPointer<vtkPolyData>::New();
    inpd->DeepCopy(surface);
    vtkSmartPointer<vtkPolyData> fullpd = vtkSmartPointer<vtkPolyData>::New();
    fullpd->DeepCopy(surface);

    // Remove cap polygons.
    if (!DeleteRegions(inpd, capFaceIDs)) {
        return nullptr;
    }

    // Remove unused vertices.
    auto cleaned = sys_geom_Clean(inpd);

    // Recap open surface.
    //
    int numCapCenterIds; 
    int *capCenterIds;
    auto capped = sys_geom_cap(cleaned, &numCapCenterIds, &capCenterIds, 1);
    std::cout << msg << "numCapCenterIds: " << numCapCenterIds << std::endl;
    std::cout << msg << "capCenterIds: " << std::endl;
    for (int i = 0; i < numCapCenterIds; i++) {
        std::cout << msg << capCenterIds[i] << std::endl;
    }

    // Find source and target caps center point IDs.
    //
    vtkSmartPointer<vtkIdList> sourcePtIds = vtkSmartPointer<vtkIdList>::New();
    vtkSmartPointer<vtkIdList> targetPtIds = vtkSmartPointer<vtkIdList>::New();

    int capIdsGiven = 0;
    if (sourceCapIds != NULL) {
      if (sourceCapIds->GetNumberOfIds() > 0)
        capIdsGiven = 1;
    }

    if (!capIdsGiven) {
      sourcePtIds->InsertNextId(capCenterIds[0]);
      for (int i = 1; i < numCapCenterIds; i++) {
        targetPtIds->InsertNextId(capCenterIds[i]);
      }

    } else {

      vtkSmartPointer<vtkCellLocator> locator = vtkSmartPointer<vtkCellLocator>::New();
      locator->SetDataSet(fullpd);
      locator->BuildLocator();

      int subId;
      double distance;
      double capPt[3];
      double closestPt[3];
      vtkIdType closestCell;
      vtkSmartPointer<vtkGenericCell> genericCell = vtkSmartPointer<vtkGenericCell>::New();

      for (int i = 0; i < numCapCenterIds; i++) {
          int ptId = capCenterIds[i];
          std::cout << msg << "----- ptID " << ptId << " -----" << std::endl;
          capped->GetPoint(ptId, capPt);
          locator->FindClosestPoint(capPt, closestPt, genericCell, closestCell, subId, distance);
          int capFaceId = fullpd->GetCellData()->GetArray("ModelFaceID")->GetTuple1(closestCell);
          std::cout << msg << "Cap pt: " << capPt[0] << "  " << capPt[1] << "  " << capPt[2] << std::endl;
          std::cout << msg << "closestPt: " << closestPt[0] << "  " << closestPt[1] << "  " << closestPt[2] << std::endl;
          capPts.push_back(std::array<double,3>{capPt[0], capPt[1], capPt[2]});

          if (sourceCapIds->IsId(capFaceId) != -1) {
            sourcePtIds->InsertNextId(ptId);
            std::cout << msg << "Add source pt ID: " << ptId << std::endl;
          } else {
            targetPtIds->InsertNextId(ptId);
            std::cout << msg << "Add target pt ID: " << ptId << std::endl;
          }
        }
    }

    auto centerlines = CalculateCenterlines(capped, sourcePtIds, targetPtIds);
    return centerlines;

    //return nullptr;
    //return capped;
    //return cleaned;
    //return inpd;
}


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
   
      return;

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
  if (argc != 2) {
    std::cout << "Usage: " << argv[0] << " SURACE_FILE_NAME(.vtp) " << std::endl;
    return EXIT_FAILURE;
  }

  // Add a renderer.
  vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
  renderer->SetBackground(1.0, 1.0, 1.0); 

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
  renderer->AddActor(gr_surf);

  // Set up data to reproduce sim-1d-kawa-my-test/Simulations1d/test1.
  // 
  vtkSmartPointer<vtkIdList> sourceCapIds = vtkSmartPointer<vtkIdList>::New();
  sourceCapIds->InsertId(0, 16);
  std::vector<int> capFaceIDs{ 9, 10, 11, 12, 13, 14, 15, 16, 17 };
  std::vector<std::array<double,3>> capPts;
  auto new_surf = CreateCenterlines_nocap(surface, sourceCapIds, capFaceIDs, capPts);
  //auto new_surf = CreateCenterlines(surface, sourceCapIds, capFaceIDs, capPts);
  if (new_surf != nullptr) { 
      std::cout << "New Surface: " << std::endl;
      std::cout << "   Number of vertices " << new_surf->GetNumberOfPoints() << std::endl;
      std::cout << "   Number of polygons " << new_surf->GetNumberOfPolys() << std::endl;
      auto gr_new_surf = create_graphics_geometry(new_surf);
      gr_new_surf->GetProperty()->SetColor(0.8, 0.0, 0.0);
      gr_new_surf->GetProperty()->SetRepresentationToWireframe();
      renderer->AddActor(gr_new_surf);
  }

  std::cout << "Cap pts: " << std::endl;
  double radius = 0.03;
  for (auto const& pt : capPts) {
      std::cout << pt[0] << "  ";
      std::cout << pt[1] << "  ";
      std::cout << pt[2] << "  " << std::endl;
      auto sphere = vtkSmartPointer<vtkSphereSource>::New();
      sphere->SetCenter(pt[0], pt[1], pt[2]);
      sphere->SetRadius(radius);
      vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
      mapper->SetInputConnection(sphere->GetOutputPort());
      vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
      actor->SetMapper(mapper);
      actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
      renderer->AddActor(actor);
  }

  // Add a render window.
  vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(1000, 1000); 

  // Add window interactor to use trackball and intercept key presses.
  //
  vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  renderWindowInteractor->SetRenderWindow(renderWindow);
  vtkSmartPointer<MouseInteractorStyle> style = vtkSmartPointer<MouseInteractorStyle>::New();
  //style->AddClEdit(clEdit);
  renderWindowInteractor->SetInteractorStyle(style);
  style->SetDefaultRenderer(renderer);
  renderWindowInteractor->SetInteractorStyle(style);

  renderWindowInteractor->Initialize();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
