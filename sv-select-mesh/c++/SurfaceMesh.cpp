
#include <iostream>
#include <string>
#include "SurfaceMesh.h"

#include <vtkCellData.h>
#include <vtkPointData.h>
#include <vtkXMLPolyDataReader.h>

//----------
// readMesh
//----------
//
void SurfaceMesh::ReadMesh(const std::string fileName)
{
  std::cout << "Read surface mesh: " << fileName << std::endl;
  m_Polydata = vtkSmartPointer<vtkPolyData>::New();

  vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();

  m_Polydata->DeepCopy(reader->GetOutput());
  vtkIdType m_NumPoints = m_Polydata->GetNumberOfPoints();
  vtkIdType m_NumPolys = m_Polydata->GetNumberOfPolys();
  std::cout << "  Number of points: " << m_NumPoints << std::endl;
  std::cout << "  Number of polygons: " << m_NumPolys << std::endl;
}

//----------
// FindData
//----------
//
void SurfaceMesh::FindData()
{
  m_PointDataNames.clear();
  vtkIdType numPointArrays = m_Polydata->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of point data arrays: " << numPointArrays << std::endl;
  std::cout << "Point data array names: " << std::endl;
  for (vtkIdType i = 0; i < numPointArrays; i++) {
    int type = m_Polydata->GetPointData()->GetArray(i)->GetDataType();
    auto name = m_Polydata->GetPointData()->GetArrayName(i);
    auto data = m_Polydata->GetPointData()->GetArray(i);
    //auto size = data->m_Polydata->GetPointData();
    std::cout << "  " << i+1 << ": " << name << " type: " << type << std::endl;
    m_PointDataNames.insert(name);
  }

  vtkIdType numCellArrays = m_Polydata->GetCellData()->GetNumberOfArrays();
  std::cout << "Number of cell data arrays: " << numCellArrays << std::endl;
}

void SurfaceMesh::CheckNodeIDs()
{
  std::cout << "---------- Checking node IDs ---------- " << std::endl;
  auto nodeIDs = vtkIntArray::SafeDownCast(m_Polydata->GetPointData()->GetArray("GlobalNodeID"));
  auto numIDs = nodeIDs->GetNumberOfTuples();
  std::cout << "Number of node IDs: " << numIDs << std::endl;
  auto numPoints = m_Polydata->GetNumberOfPoints();
  auto points = m_Polydata->GetPoints();
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
              std::cout << i << ": pt1 " << pt1[0] << " " << pt1[1] << " " << pt1[2] << std::endl;
              std::cout << j << ": pt2 " << pt2[0] << " " << pt2[1] << " " << pt2[2] << std::endl;
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
vtkSmartPointer<vtkDoubleArray> SurfaceMesh::GetDataArray(std::string name) 
{
  return vtkDoubleArray::SafeDownCast(m_Polydata->GetPointData()->GetArray(name.c_str()));
}


//-----------
// IsSurface
//-----------
bool SurfaceMesh::IsSurface()
{
  return true;
}

//---------
// GetMesh
//---------
vtkSmartPointer<vtkDataSet> SurfaceMesh::GetMesh()
{
    return m_Polydata;
}

//-------------
// GetPolyData
//-------------
//
vtkSmartPointer<vtkPolyData> SurfaceMesh::GetPolyData()
{
  return m_Polydata;
}

//-------------
// AddGeometry
//-------------
//
void SurfaceMesh::AddGeometry(Graphics& graphics)
{
  auto geom = graphics.CreateGeometry(m_Polydata);
  geom->GetProperty()->SetColor(0.8, 0.0, 0.0);
  //geom->GetProperty()->SetRepresentationToWireframe();
  geom->GetProperty()->EdgeVisibilityOn();
  graphics.AddGeometry(geom);
}

