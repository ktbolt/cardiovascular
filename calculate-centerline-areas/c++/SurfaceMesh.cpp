
#include <iostream>
#include <string>
#include "Slice.h"
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
#include <vtkSphereSource.h>
#include <vtkStripper.h>
#include <vtkTriangle.h>
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
  m_MeshFileName = fileName;
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

  // Create a cell locator used to interpolate data 
  // at slice points on the surface.
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
  std::cout << "Surface point data arrays: " << numPointArrays << std::endl;
  std::cout << "  Number of point data arrays: " << numPointArrays << std::endl;
  std::cout << "  Point data array namess: " << std::endl;
  for (vtkIdType i = 0; i < numPointArrays; i++) {
    auto name = m_Polydata->GetPointData()->GetArrayName(i);
    int type = m_Polydata->GetPointData()->GetArray(i)->GetDataType();
    auto numComp = m_Polydata->GetPointData()->GetArray(i)->GetNumberOfComponents();
    std::cout << "    " << i+1 << ": " << name << " type: " << type << "  numComp: " << numComp << std::endl;
    m_PointDataNames.insert(name);
  }

  vtkIdType numCellArrays = m_Polydata->GetCellData()->GetNumberOfArrays();
  std::cout << "  Number of cell data arrays: " << numCellArrays << std::endl;
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
// Slice the surface mesh with a plane.
//
void SurfaceMesh::SlicePlane(int index, int cellID, std::string dataName, double pos[3], double normal[3]) 
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

  // Create a Slice object to store slice data.
  auto slice = new Slice(index, cellID, dataName, pos);
  m_Slices.push_back(slice);

  // Calculate the area of the slice.
  SliceArea(lines, slice);

  // Interpolate the surface data to the slice points.
  Interpolate(dataName, lines, slice);
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

//---------------------------
// CalculateCenterlinesRadii
//---------------------------
//
void SurfaceMesh::CalculateCenterlinesRadii(Centerlines& centerlines)
{
  std::cout << std::endl;
  std::cout << "---------- Calculate Centerlines Radii ----------" << std::endl;

  for(vtkIdType n = 0; n < centerlines.m_Polydata->GetNumberOfPoints(); n++) {
  }


}

//-------------
// WriteSlices
//-------------
//
void SurfaceMesh::WriteSlices()
{
  std::cout << std::endl;
  std::cout << "---------- Write Slices ----------" << std::endl;

  if (m_Slices.size() == 0) {
    std::cout << "No slices to write. " << std::endl;
    return;
  }

  if (m_Slices[0]->m_DataName == "") {
    std::cout << "No data to write. " << std::endl;
    return;
  }

  auto dataName = m_Slices[0]->m_DataName;
  auto filePrefix = m_MeshFileName.substr(0,m_MeshFileName.find_last_of(".") - 1);
  auto fileName = filePrefix + "_" + dataName + ".txt";
  std::cout << "Writing " << m_Slices.size() << " slices to '" << fileName << "'" << std::endl; 

  ofstream file;
  file.open (fileName);
  file << "# Slices file" << std::endl;
  file << "data name: " << dataName << std::endl;
  file << "number of slices: " << m_Slices.size() << std::endl;

  int sliceNum = 1;
  for (auto const& slice :  m_Slices) {
    file << " " << std::endl;
    file << "slice " << sliceNum << std::endl;
    slice->Write(file);
    sliceNum += 1;
  }

  file.close();
}

//-------------
// Interpolate
//-------------
// Interpolate the surface mesh data.
//
// Arguments:
//
//   lines: The geometry of the intersection of the surface with a slice plane.
//
//
// For each point in 'lines' determine the cell the point lies in using
// m_CellLocator->FindCell(). This function returns the triangle local 
// coordinates (r,s) of the point and weights the point in the triangle and 
//
//
void SurfaceMesh::Interpolate(std::string dataName, vtkPolyData* lines, Slice* slice) 
{
  auto debugInterpolate = false;

  std::cout << "---------- Interpolate ----------" << std::endl;
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
    slice->AddPoint(pt);
    auto cellID = m_CellLocator->FindCell(pt, tol2, cell, localCoords, weights);
    auto numPts = cell->GetNumberOfPoints();
    auto nodeIDs = vtkIntArray::SafeDownCast(m_Polydata->GetPointData()->GetArray("GlobalNodeID"));
    auto elemIDs = vtkIntArray::SafeDownCast(m_Polydata->GetCellData()->GetArray("GlobalElementID"));
    auto elemID = elemIDs->GetValue(cellID);

    if (debugInterpolate) {
      std::cout << "--------------- Sample " << i << " ----------" << std::endl;
      std::cout << "Sample point: " << pt[0] << "  " << pt[1] << "  " << pt[2] << std::endl;
      std::cout << "CellID: " << cellID << std::endl;
      std::cout << "  localCoords: " << localCoords[0] << "  " << localCoords[1] << "  " << std::endl;
      std::cout << "  weights: " << weights[0] << "  " << weights[1] << "  " << weights[2] << std::endl;
      std::cout << "  Elem ID: " << elemID << std::endl;
      std::cout << "  Number of cell points: " << numPts << std::endl;
      std::cout << "  Connectivity: ";
      for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
        auto id = cell->PointIds->GetId(pointInd);
        auto nodeID = nodeIDs->GetValue(id);
        std::cout << nodeID << " ";
      }
      std::cout << std::endl;

      // Check that weights interpolate points.
      if (false) {
        double p0[3], p1[3], p2[3];
        vtkCell* tcell = dynamic_cast<vtkCell*>(cell);
        tcell->GetPoints()->GetPoint(0, p0);
        tcell->GetPoints()->GetPoint(1, p1);
        tcell->GetPoints()->GetPoint(2, p2);
        double w1, w2, w3, ipt[3];
        w1 = weights[0];
        w2 = weights[1];
        w3 = weights[2];
        ipt[0] = 0.0;
        ipt[1] = 0.0;
        ipt[2] = 0.0;
        for (int k = 0; k < 3; k++) {
          ipt[k] = w1*p0[k] + w2*p1[k] + w3*p2[k];
        }
        std::cout << "  interp point: " << ipt[0] << "  " << ipt[1] << "  " << ipt[2] << std::endl;
      }
    }

    if (dataName == "") {
      return;
    }

    
    // Interpolate data at the slice sample points.
    //
    auto numComp = data->GetNumberOfComponents();

    if (debugInterpolate) {
      std::cout << "Cell Data: " << std::endl;
      std::cout << "  Name: " << dataName << std::endl;
      std::cout << "  Number of components: " << numComp << std::endl;
    }

    double idata[3] = {0.0, 0.0, 0.0};

    for (vtkIdType pointInd = 0; pointInd < numPts; ++pointInd) {
      auto id = cell->PointIds->GetId(pointInd);
      auto nodeID = nodeIDs->GetValue(id);
      if (numComp == 1) {
        double value = data->GetValue(id);
        idata[0] += weights[pointInd]*value;
        if (debugInterpolate) {
          std::cout << "  ID: " << nodeID << "   Value: " << value << std::endl;
        }
      } else if (numComp == 3) {
        auto v1 = data->GetComponent(id, 0);
        auto v2 = data->GetComponent(id, 1);
        auto v3 = data->GetComponent(id, 2);
        idata[0] += weights[pointInd]*v1;
        idata[1] += weights[pointInd]*v2;
        idata[2] += weights[pointInd]*v3;
        if (debugInterpolate) {
          std::cout << "  Node ID: " << nodeID << "   Values: " << v1 << " " << v2 << " " << v3 << std::endl;
        }
      }
    }
 
    if (numComp == 1) {
        slice->AddScalarData(idata[0]);
    } else if (numComp == 3) {
        slice->AddVectorData(idata);
    }

  }  // for (vtkIdType i = 0; i < points->GetNumberOfPoints(); i++) 

}

//-----------
// SliceArea
//-----------
//
// Compute the area of a surface slice.
//
void SurfaceMesh::SliceArea(vtkPolyData* lines, Slice* slice) 
{
  auto points = lines->GetPoints();
  vtkSmartPointer<vtkPolyData> polydata = vtkSmartPointer<vtkPolyData>::New();
  polydata->SetPoints(points);
  vtkSmartPointer<vtkDelaunay2D> delaunay = vtkSmartPointer<vtkDelaunay2D>::New();
  delaunay->SetInputData(polydata);

  vtkSmartPointer<vtkMassProperties> massProperties = vtkSmartPointer<vtkMassProperties>::New();
  massProperties->SetInputConnection(delaunay->GetOutputPort());
  massProperties->Update();
  slice->area = massProperties->GetSurfaceArea();
  std::cout <<  "Area:   " << slice->area << std::endl;
  auto radius = sqrt(slice->area/M_PI);
  std::cout <<  "Area equivalent radius:   " << radius << std::endl;

  // Show the cross section area.
  //
  vtkSmartPointer<vtkPolyDataMapper> meshMapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  meshMapper->SetInputConnection(delaunay->GetOutputPort());
  vtkSmartPointer<vtkActor> meshActor = vtkSmartPointer<vtkActor>::New();
  meshActor->SetMapper(meshMapper);
  //meshActor->GetProperty()->EdgeVisibilityOn();
  meshActor->GetProperty()->SetColor(0.8, 0.0, 0.0);
  m_Graphics->AddGeometry(meshActor);
  slice->meshActor = meshActor; 

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
  slice->pointActor = pointActor; 

  // Add a sphere to visualize radius.
  auto sphere = vtkSmartPointer<vtkSphereSource>::New();
  sphere->SetCenter(slice->m_CenterlinePosition[0], slice->m_CenterlinePosition[1], 
                    slice->m_CenterlinePosition[2]);
  sphere->SetRadius(radius);
  sphere->SetThetaResolution(32);
  sphere->SetPhiResolution(32);
  vtkSmartPointer<vtkPolyDataMapper> sphereMapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  sphereMapper->SetInputConnection(sphere->GetOutputPort());
  vtkSmartPointer<vtkActor> sphereActor = vtkSmartPointer<vtkActor>::New();
  sphereActor->SetMapper(sphereMapper);
  sphereActor->GetProperty()->SetColor(0.0, 0.0, 1.0);
  //m_Graphics->AddGeometry(sphereActor);
  slice->sphereActor = sphereActor; 

}

//-----------
// UndoSlice
//-----------
//
void SurfaceMesh::UndoSlice()
{
  if (m_Slices.size() == 0) {
    return;
  }
  std::cout << std::endl << ">>> Remove last slice." << std::endl;
  auto slice = m_Slices.back();
  m_Slices.pop_back();
  slice->pointActor->SetVisibility(false);
  slice->meshActor->SetVisibility(false);
  slice->sphereActor->SetVisibility(false);
  m_Graphics->Refresh();
}
