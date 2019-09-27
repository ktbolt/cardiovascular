
#include <iostream>
#include <string>
#include <array>
#include "VolumeMesh.h"

#include <vtkCellData.h>
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
    m_PointDataNames.insert(name);
  }

  vtkIdType numCellArrays = m_Mesh->GetCellData()->GetNumberOfArrays();
  std::cout << "Number of cell data arrays: " << numCellArrays << std::endl;
}

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
          if ((dx*dx == 0.0) && (dy*dy == 0.0) && (dz*dz == 0.0)) {
              //std::cout << i << ": pt1 " << pt1[0] << " " << pt1[1] << " " << pt1[2] << std::endl;
              //std::cout << j << ": pt2 " << pt2[0] << " " << pt2[1] << " " << pt2[2] << std::endl;
              m_DupeCoords.push_back(std::array<double,3>{{pt1[0], pt1[1], pt1[2]}});
              numDupe += 1;
          }
      }
  }

  std::cout << "Number of duplicate coordinates: " << numDupe << std::endl;
}

//--------------
// GetDataArray
//--------------
//
vtkSmartPointer<vtkDoubleArray> VolumeMesh::GetDataArray(std::string name) 
{
  return vtkDoubleArray::SafeDownCast(m_Mesh->GetPointData()->GetArray(name.c_str()));
}


//-----------
// IsVolume
//-----------
//
bool VolumeMesh::IsVolume()
{
  return true;
}

bool VolumeMesh::IsSurface()
{
  return false;
}


//---------
// GetMesh
//---------
vtkSmartPointer<vtkDataSet> VolumeMesh::GetMesh()
{
    return m_Mesh;
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

  return triangleFilter->GetOutput();
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
  geom->GetProperty()->SetRepresentationToWireframe();
  geom->GetProperty()->EdgeVisibilityOn();
  graphics.AddGeometry(geom);
}

