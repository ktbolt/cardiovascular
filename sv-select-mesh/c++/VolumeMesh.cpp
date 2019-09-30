
#include <iostream>
#include <string>
#include <array>
#include "VolumeMesh.h"

#include <vtkAppendFilter.h>
#include <vtkCellData.h>
#include <vtkCleanPolyData.h>
#include <vtkGenericCell.h>
#include <vtkPointData.h>
#include <vtkGeometryFilter.h>
#include <vtkTriangleFilter.h>
#include <vtkXMLUnstructuredGridReader.h>

//----------
// readMesh
//----------
//
void VolumeMesh::ReadMesh(const std::string fileName)
{
  std::cout << "Read volume mesh: " << fileName << std::endl;
  m_Mesh = vtkSmartPointer<vtkUnstructuredGrid>::New();

  vtkSmartPointer<vtkXMLUnstructuredGridReader> reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();
  m_Mesh->DeepCopy(reader->GetOutput());

  vtkIdType m_NumPoints = m_Mesh->GetNumberOfPoints();
  vtkIdType m_NumCells = m_Mesh->GetNumberOfCells();
  std::cout << "  Number of points: " << m_NumPoints << std::endl;
  std::cout << "  Number of cells: " << m_NumCells << std::endl;
}

//----------
// FindData
//----------
//
void VolumeMesh::FindData()
{
  m_PointDataNames.clear();
  vtkIdType numPointArrays = m_Mesh->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of point data arrays: " << numPointArrays << std::endl;
  std::cout << "Point data array names: " << std::endl;
  for (vtkIdType i = 0; i < numPointArrays; i++) {
    int type = m_Mesh->GetPointData()->GetArray(i)->GetDataType();
    auto name = m_Mesh->GetPointData()->GetArrayName(i);
    auto data = m_Mesh->GetPointData()->GetArray(i);
    //auto size = data->m_Mesh->GetPointData();
    std::cout << "  " << i+1 << ": " << name << " type: " << type << std::endl;

    if (!strcmp(name, "GlobalNodeID")) {
        auto nodeIDs = vtkIntArray::SafeDownCast(m_Mesh->GetPointData()->GetArray("GlobalNodeID"));
        std::vector<int> ids;
        for (int i = 0; i < nodeIDs->GetNumberOfTuples(); i++) {
            auto id = nodeIDs->GetValue(i);
            ids.push_back(id);
        }
        std::sort(ids.begin(), ids.end());
        std::cout << "    Number of IDs: " << ids.size() << std::endl;
        std::cout << "    ID range: " << ids[0] << ", " << ids.back() << std::endl;
    }
    m_PointDataNames.insert(name);
  }

  vtkIdType numCellArrays = m_Mesh->GetCellData()->GetNumberOfArrays();
  std::cout << "Number of cell data arrays: " << numCellArrays << std::endl;
  std::cout << "Cell data array names: " << std::endl;
  for (vtkIdType i = 0; i < numCellArrays; i++) {
    int type = m_Mesh->GetCellData()->GetArray(i)->GetDataType();
    auto name = m_Mesh->GetCellData()->GetArrayName(i);
    auto data = m_Mesh->GetCellData()->GetArray(i);
    std::cout << "  " << i+1 << ": " << name << " type: " << type << std::endl;
  }
}

//--------------
// CheckNodeIDs
//--------------
//
void VolumeMesh::CheckNodeIDs()
{
  std::cout << "---------- Checking node IDs ---------- " << std::endl;
  auto nodeIDs = vtkIntArray::SafeDownCast(m_Mesh->GetPointData()->GetArray("GlobalNodeID"));
  auto numIDs = nodeIDs->GetNumberOfTuples();
  std::cout << "Number of node IDs: " << numIDs << std::endl;
  auto numPoints = m_Mesh->GetNumberOfPoints();
  auto points = m_Mesh->GetPoints();
  std::cout << "Number of coordinates: " << numPoints << std::endl;
  double pt1[3], pt2[3];
  int numDupe = 0;

  for (int i = 0; i < numPoints; i++) {
      points->GetPoint(i,pt1);
      for (int j = i+1; j < numPoints; j++) {
          points->GetPoint(j,pt2);
          auto dx = pt1[0] - pt2[0];
          auto dy = pt1[1] - pt2[1];
          auto dz = pt1[2] - pt2[2];
          auto d = sqrt(dx*dx + dy*dy + dz*dz);
          if (d < 1e-6) {
              //std::cout << i << ": pt1 " << pt1[0] << " " << pt1[1] << " " << pt1[2] << std::endl;
              //std::cout << j << ": pt2 " << pt2[0] << " " << pt2[1] << " " << pt2[2] << std::endl;
              m_DupeCoords.push_back(std::array<double,3>{{pt1[0], pt1[1], pt1[2]}});
              m_DupeNodeIDs[j] = i;
              numDupe += 1;
          }
      }
  }

  std::cout << "Number of duplicate coordinates: " << numDupe << std::endl;
  std::cout << "Number of duplicate node IDs: " << m_DupeNodeIDs.size() << std::endl;
}

//---------
// FixMesh
//---------
//
// Fix up the mesh connectivity the hard way.
//
// [TODO:DaveP] I never finished this, found a solution in SV using vtkAppendFilter.
//
void VolumeMesh::FixMesh()
{ 
  std::cout << "---------- Fix Mesh ---------- " << std::endl;
  auto nodeIDs = vtkIntArray::SafeDownCast(m_Mesh->GetPointData()->GetArray("GlobalNodeID"));
  auto numIDs = nodeIDs->GetNumberOfTuples();
  auto numPoints = m_Mesh->GetNumberOfPoints();
  auto points = m_Mesh->GetPoints();

  // Create new unique points and a map between old and new node numbering.
  //
  int numNewNodes = 0;
  std::vector<std::array<double,3>> newNodes;
  std::map<int,int> oldToNewNodeIDsMap;

  for (int i = 0; i < numPoints; i++) {
      if (!m_DupeNodeIDs.count(i)) {
          double pt[3];
          points->GetPoint(i, pt);
          newNodes.push_back(std::array<double,3>({{pt[0],pt[1],pt[2]}}));
          oldToNewNodeIDsMap[i] = i;
          //oldToNewNodeIDsMap[i] = numNewNodes;
          numNewNodes += 1;
      } else {
          oldToNewNodeIDsMap[i] = oldToNewNodeIDsMap[m_DupeNodeIDs[i]];
      }
  }

  std::cout << "Number of new nodes: " << newNodes.size() << std::endl;
 
  // Change element connectivity to reference new nodes.
  //
  vtkIdType numCells = m_Mesh->GetNumberOfCells();
  vtkCellArray* cells = m_Mesh->GetCells();
  vtkUnsignedCharArray* cellTypes = m_Mesh->GetCellTypesArray();
  vtkGenericCell* cell = vtkGenericCell::New();
  std::cout << "Number of elements: " << numCells << std::endl;

  vtkIdType ids[6];
  vtkIdType loc = 0;

  for (vtkIdType cellId = 0; cellId < numCells; cellId++) {
      m_Mesh->GetCell(cellId, cell);
      auto dim = cell->GetCellDimension();
      auto numPts = cell->GetNumberOfPoints();
      for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
          auto id = cell->PointIds->GetId(pointInd);
          auto newID = oldToNewNodeIDsMap[id];
          //ids[pointInd] = id;
          ids[pointInd] = newID;
      }

    cells->ReplaceCell(loc, numPts, ids);
    loc += numPts + 1;
  }

  // Add new points.
  vtkPoints* newPoints = vtkPoints::New();
  newPoints->SetNumberOfPoints(numNewNodes);
  for (auto const& pt : newNodes) {
      newPoints->InsertNextPoint(pt[0], pt[1], pt[2]);
  }
  //m_Mesh->SetPoints(newPoints);

  for (int i = 0; i < numNewNodes; i++) {
      double pt[3];
      pt[0] = newNodes[i][0];
      pt[1] = newNodes[i][1];
      pt[2] = newNodes[i][2];
      points->GetPoint(i, pt);
  }

  m_Mesh->GetPoints()->Modified();

  m_Mesh->Modified();
}

//--------------
// GetDataArray
//--------------
//
vtkSmartPointer<vtkDoubleArray> VolumeMesh::GetDataArray(std::string name) 
{
  return vtkDoubleArray::SafeDownCast(m_Mesh->GetPointData()->GetArray(name.c_str()));
}

bool VolumeMesh::IsSurface()
{
  return false;
}

//---------
// GetMesh
//---------
//
vtkSmartPointer<vtkDataSet> VolumeMesh::GetMesh()
{
    return m_Polydata;
    //return m_Mesh;
}

//-------------
// GetPolyData
//-------------
//
vtkSmartPointer<vtkPolyData> VolumeMesh::GetPolyData()
{
  // Convert mesh to polydata.
  vtkSmartPointer<vtkGeometryFilter> geometryFilter = vtkSmartPointer<vtkGeometryFilter>::New();
  geometryFilter->SetInputData(m_Mesh);
  geometryFilter->Update(); 
  vtkPolyData* meshPolyData = geometryFilter->GetOutput();

  vtkSmartPointer<vtkTriangleFilter> triangleFilter = vtkSmartPointer<vtkTriangleFilter>::New();
  triangleFilter->SetInputData(meshPolyData);
  triangleFilter->Update();
  m_Polydata = triangleFilter->GetOutput();
  std::cout << "Mesh Polydata: " << std::endl;
  std::cout << "  Number of points: " << m_Polydata->GetNumberOfPoints() << std::endl;
  std::cout << "  Number of polygons: " << m_Polydata->GetNumberOfPolys() << std::endl;

  // Could never get vtkCleanPolyData to work.
  /*
  vtkSmartPointer<vtkCleanPolyData> cleanFilter = vtkSmartPointer<vtkCleanPolyData>::New();
  cleanFilter->ToleranceIsAbsoluteOn();
  cleanFilter->SetPointMerging(true);
  double tol = 1e-6;
  cleanFilter->SetAbsoluteTolerance(tol);
  cleanFilter->SetInputConnection(triangleFilter->GetOutputPort());
  cleanFilter->Update();
  m_Polydata = cleanFilter->GetOutput();

  std::cout << "Cleaned Polydata: " << std::endl;
  std::cout << "  Number of points: " << m_Polydata->GetNumberOfPoints() << std::endl;
  std::cout << "  Number of polygons: " << m_Polydata->GetNumberOfPolys() << std::endl;
  */

  // The vtkAppendFilter does work, creates a mesh with unique points.
  /* 
  vtkSmartPointer<vtkAppendFilter> appendFilter = vtkSmartPointer<vtkAppendFilter>::New();
  appendFilter->AddInputData(m_Polydata);
  appendFilter->SetMergePoints(true);
  appendFilter->Update();
  vtkSmartPointer<vtkUnstructuredGrid> combined = appendFilter->GetOutput();
  std::cout << "There are " << combined->GetNumberOfPoints() << " points combined." << std::endl;
  */

  return m_Polydata; 
}

//-------------
// AddGeometry
//-------------
//
void VolumeMesh::AddGeometry(Graphics& graphics)
{
  auto polyData = GetPolyData();
  auto geom = graphics.CreateGeometry(polyData);
  geom->GetProperty()->SetColor(0.8, 0.0, 0.0);
  //geom->GetProperty()->SetRepresentationToWireframe();
  geom->GetProperty()->EdgeVisibilityOn();
  graphics.AddGeometry(geom);
}

