
#include <iostream>
#include <string>
#include "SurfaceMesh.h"

#include <vtkActor.h>
#include <vtkCellData.h>
#include <vtkCutter.h>
#include <vtkDataArray.h>
#include <vtkDelaunay2D.h>
#include <vtkDoubleArray.h>
#include <vtkGenericCell.h>
#include <vtkFillHolesFilter.h>
#include <vtkMassProperties.h>
#include <vtkMath.h>
#include <vtkPlane.h>
#include <vtkPointData.h>
#include <vtkPolyDataMapper.h>
#include <vtkPolyDataNormals.h>
#include <vtkProbeFilter.h>
#include <vtkStripper.h>
#include <vtkTriangleFilter.h>
#include <vtkVertexGlyphFilter.h>
#include <vtkXMLPolyDataReader.h>

SurfaceMesh::SurfaceMesh()
{
  m_CellLocator = vtkSmartPointer<vtkCellLocator>::New();
}

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

  m_CellLocator->SetDataSet(m_Polydata);
  m_CellLocator->BuildLocator();
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
    auto name = m_Polydata->GetPointData()->GetArrayName(i);
    int type = m_Polydata->GetPointData()->GetArray(i)->GetDataType();
    auto numComp = m_Polydata->GetPointData()->GetArray(i)->GetNumberOfComponents();
    std::cout << "  " << i+1 << ": " << name << " type: " << type << "  numComp: " << numComp << std::endl;
    m_PointDataNames.insert(name);
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
  //geom->GetProperty()->EdgeVisibilityOn();
  geom->GetProperty()->SetColor(0.8, 0.8, 0.8);
  geom->GetProperty()->SetOpacity(0.5);
  //geom->GetProperty()->SetRepresentationToWireframe();
  //geom->GetProperty()->FrontfaceCullingOn();
  //geom->GetProperty()->BackfaceCullingOn();
  geom->PickableOff();
  graphics.AddGeometry(geom);
}

//------------
// SlicePlane
//------------
//
void SurfaceMesh::SlicePlane(std::string dataName, double pos[3], double normal[3]) 
{
  std::cout << "---------- Slice Surface ----------" << std::endl;

  // Slice surface.
  //
  vtkSmartPointer<vtkPlane> plane = vtkSmartPointer<vtkPlane>::New();
  plane->SetOrigin(pos);
  plane->SetNormal(normal[0], normal[1], normal[2]); 

  vtkSmartPointer<vtkCutter> cutter = vtkSmartPointer<vtkCutter>::New();
  cutter->SetInputData(m_Polydata);
  cutter->SetCutFunction(plane);
  cutter->GenerateValues(1, 0.0, 0.0);

  // Show slice.
  //
  auto showSlice = false;

  if (showSlice) { 
    vtkSmartPointer<vtkPolyDataMapper> cutterMapper = vtkSmartPointer<vtkPolyDataMapper>::New();
    cutterMapper->SetInputConnection(cutter->GetOutputPort());
    cutterMapper->ScalarVisibilityOff();
    //
    vtkSmartPointer<vtkActor> cutterActor = vtkSmartPointer<vtkActor>::New();
    cutterActor->GetProperty()->SetColor(1.0, 0.0, 0.0);
    cutterActor->GetProperty()->SetLineWidth(2);
    cutterActor->SetMapper(cutterMapper);
    m_Graphics->AddGeometry(cutterActor);
  }

  // Get a single Polydata lines geometry from the slice.
  auto lines = GetSliceLines(cutter, pos);

  // Calculate the area of the slice.
  SliceArea(lines);

  // Interpolate the surface data to the slice points.
  Interpolate(dataName, lines);
}

//-----------
// SliceLine
//-----------
//
void SurfaceMesh::SliceLine(std::string dataName, double pos[3], double normal[3])
{
  double startRay[3];
  double endRay[3];
  double v2[3], v3[3];

  vtkMath::Perpendiculars(normal, v2, NULL, 0);
  vtkMath::Cross(normal, v2, v3);

  int numPts = 20;

  for (int i = 0; i < 3; i++) {
    startRay[i] = pos[i];
    //endRay[i] = pos[i] + r*v2[i];
  }

}

//---------------
// GetSliceLines
//---------------
// Get a single Polydata lines geometry from the slice.
//
vtkSmartPointer<vtkPolyData> SurfaceMesh::GetSliceLines(vtkSmartPointer<vtkCutter> cutter, double pos[3]) 
{
  // Get the Polydata lines geometry for the slice.
  //
  vtkSmartPointer<vtkStripper> stripper = vtkSmartPointer<vtkStripper>::New();
  stripper->SetInputConnection(cutter->GetOutputPort());
  stripper->Update();
  auto linesPolyData = stripper->GetOutput();

  // Find the slice for the centerline point selected.
  //
  double pt[3];
  double center[3] = {0.0, 0.0, 0.0};
  double min_d = 1e9;
  double min_i = 0;

  for (vtkIdType i = 0; i < linesPolyData->GetNumberOfCells(); i++) {
    auto cell = linesPolyData->GetCell(i);
    auto points = cell->GetPoints();
    auto numPoints = cell->GetNumberOfPoints();
    //std::cout << "Number of points: " << numPoints << std::endl;
    for (int j = 0; j < numPoints; j++) { 
      points->GetPoint(j, pt);
      center[0] += pt[0];
      center[1] += pt[1];
      center[2] += pt[2];
    }
    center[0] /= numPoints; 
    center[1] /= numPoints; 
    center[2] /= numPoints; 
    auto dx = center[0] - pos[0];
    auto dy = center[1] - pos[1];
    auto dz = center[2] - pos[2];
    auto d = sqrt(dx*dx + dy*dy + dz*dz);
    //std::cout << "Center: " << center[0] << "  " << center[1] << "  " << center[2] << std::endl;
    //std::cout << "Pos: " << pos[0] << "  " << pos[1] << "  " << pos[2] << std::endl;
    //std::cout << "d: " << d << std::endl;
    if (d < min_d) {
      min_d = d;
      min_i = i;
    }
  }

  auto cell = linesPolyData->GetCell(min_i);
  auto points = cell->GetPoints();
  vtkSmartPointer<vtkPolyData> sliceLines = vtkSmartPointer<vtkPolyData>::New();
  sliceLines->SetPoints(points);

  return sliceLines;
}

//-------------
// Interpolate
//-------------
// Interpolate the surface mesh data.
//
void SurfaceMesh::Interpolate(std::string dataName, vtkPolyData* lines) 
{
  auto numLines = lines->GetNumberOfLines();
  auto numPoints = lines->GetNumberOfPoints();
  auto points = lines->GetPoints();
  std::cout << "Number of points: " << numPoints << std::endl;

  double tol2 = 1e-6;
  double localCoords[2];
  double weights[3]; 
  vtkGenericCell* cell = vtkGenericCell::New();
  auto data = GetDataArray(dataName);

  for (vtkIdType i = 0; i < points->GetNumberOfPoints(); i++) {
    double pt[3];
    points->GetPoint(i,pt);
    auto cellID = m_CellLocator->FindCell(pt, tol2, cell, localCoords, weights);
    //std::cout << i << ": " << pt[0] << "  " << pt[1] << "  " << pt[2] << std::endl;
    //std::cout << "    cellID: " << cellId << std::endl;
    //std::cout << "    localCoords: " << localCoords[0] << "  " << localCoords[1] << "  " << std::endl;
    //std::cout << "    weights: " << weights[0] << "  " << weights[1] << "  " << weights[2] << std::endl;

    auto numPts = cell->GetNumberOfPoints();
    auto nodeIDs = vtkIntArray::SafeDownCast(m_Polydata->GetPointData()->GetArray("GlobalNodeID"));
    auto elemIDs = vtkIntArray::SafeDownCast(m_Polydata->GetCellData()->GetArray("GlobalElementID"));
    auto elemID = elemIDs->GetValue(cellID);
    //std::cout << "--------------------" << std::endl;
    //std::cout << "Cell ID is: " << cellID << std::endl;
    //std::cout << "  Elem ID: " << elemID << std::endl;
    //std::cout << "  Number of cell points: " << numPts << std::endl;
    //std::cout << "  Connectivity: ";
    for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
      auto id = cell->PointIds->GetId(pointInd);
      auto nodeID = nodeIDs->GetValue(id);
      //std::cout << nodeID << " ";
   }
   //std::cout << std::endl;

   if (dataName != "") {
     //std::cout << "Cell Data: " << std::endl;
     //std::cout << "  Name: " << dataName << std::endl;
     auto numComp = data->GetNumberOfComponents();
     //std::cout << "  Number of components: " << numComp << std::endl;

     for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
       auto id = cell->PointIds->GetId(pointInd);
       auto nodeID = nodeIDs->GetValue(id);
       if (numComp == 1) {
         double value = data->GetValue(id);
         //std::cout << "  ID: " << nodeID << "   Value: " << value << std::endl;
       } else if (numComp == 3) {
         auto v1 = data->GetComponent(id, 0);
         auto v2 = data->GetComponent(id, 1);
         auto v3 = data->GetComponent(id, 2);
         //std::cout << "  Node ID: " << nodeID << "   Values: " << v1 << " " << v2 << " " << v3 << std::endl;
       }
     }
   }
  
  }  // for (vtkIdType i = 0; i < points->GetNumberOfPoints(); i++) 

}

//-----------
// SliceArea
//-----------
//
// Compute the area of a surface slice.
//
void SurfaceMesh::SliceArea(vtkPolyData* lines) 
{
  auto points = lines->GetPoints();
  vtkSmartPointer<vtkPolyData> polydata = vtkSmartPointer<vtkPolyData>::New();
  polydata->SetPoints(points);
  vtkSmartPointer<vtkDelaunay2D> delaunay = vtkSmartPointer<vtkDelaunay2D>::New();
  delaunay->SetInputData(polydata);

  vtkSmartPointer<vtkMassProperties> massProperties = vtkSmartPointer<vtkMassProperties>::New();
  massProperties->SetInputConnection(delaunay->GetOutputPort());
  massProperties->Update();
  std::cout <<  "Area:   " << massProperties->GetSurfaceArea() << std::endl;

  // Show the cross section area.
  //
  vtkSmartPointer<vtkPolyDataMapper> meshMapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  meshMapper->SetInputConnection(delaunay->GetOutputPort());
  vtkSmartPointer<vtkActor> meshActor = vtkSmartPointer<vtkActor>::New();
  meshActor->SetMapper(meshMapper);
  //meshActor->GetProperty()->EdgeVisibilityOn();
  meshActor->GetProperty()->SetColor(0.8, 0.0, 0.0);
  m_Graphics->AddGeometry(meshActor);

  vtkSmartPointer<vtkVertexGlyphFilter> glyphFilter = vtkSmartPointer<vtkVertexGlyphFilter>::New();
  glyphFilter->SetInputData(polydata);
  vtkSmartPointer<vtkPolyDataMapper> pointMapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  pointMapper->SetInputConnection(glyphFilter->GetOutputPort());
  vtkSmartPointer<vtkActor> pointActor = vtkSmartPointer<vtkActor>::New();
  //pointActor->GetProperty()->SetColor(colors->GetColor3d("Tomato").GetData());
  pointActor->GetProperty()->SetColor(0.8, 0.8, 0.0);
  pointActor->GetProperty()->SetPointSize(5);
  pointActor->SetMapper(pointMapper);
  m_Graphics->AddGeometry(pointActor);
}

