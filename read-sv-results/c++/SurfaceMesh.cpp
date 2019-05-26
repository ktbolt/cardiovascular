
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
  std::cout << "Point data array namess: " << std::endl;
  for (vtkIdType i = 0; i < numPointArrays; i++) {
    int type = m_Polydata->GetPointData()->GetArray(i)->GetDataType();
    auto name = m_Polydata->GetPointData()->GetArrayName(i);
    std::cout << "  " << i+1 << ": " << name << " type: " << type << std::endl;
    m_PointDataNames.push_back(name);
  }

  vtkIdType numCellArrays = m_Polydata->GetCellData()->GetNumberOfArrays();
  std::cout << "Number of cell data arrays: " << numCellArrays << std::endl;
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

