
// version test

#include <iostream>
#include <string>
#include "Centerlines.h"

#include <vtkCellData.h>
#include <vtkPointData.h>
#include <vtkXMLPolyDataReader.h>

//-------------
// Centerlines
//-------------
//
Centerlines::Centerlines()
{
}

//-----------------
// ReadCenterlines
//-----------------
//
void Centerlines::ReadCenterlines(std::string fileName)
{
  std::cout << "Read centerlines: " << fileName << std::endl;
  m_Polydata = vtkSmartPointer<vtkPolyData>::New();

  vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  reader->SetFileName(fileName.c_str());
  reader->Update();

  m_Polydata->DeepCopy(reader->GetOutput());
  m_NumLineVerts = m_Polydata->GetNumberOfPoints();
  m_NumLines = m_Polydata->GetNumberOfLines();
  std::cout << "Number of vertices " << m_NumLineVerts << std::endl;
  std::cout << "Number of lines " << m_NumLines << std::endl;

  create_cell_locator();

  ShowData();
}

//-------------
// AddGeometry
//-------------
//
void Centerlines::AddGeometry(Graphics& graphics)
{
  auto geom = graphics.CreateGeometry(m_Polydata);
  geom->GetProperty()->SetColor(0.0, 0.8, 0.0);
  //geom->GetProperty()->SetRepresentationToWireframe();
  //geom->GetProperty()->EdgeVisibilityOn();
  geom->GetProperty()->SetLineWidth(4.0);
  //geom->SetPickable(0);
  graphics.AddGeometry(geom);
}

//---------
// SetMesh
//---------
//
void Centerlines::SetMesh(Mesh* mesh)
{
  m_Mesh = mesh;

  if (m_Mesh->IsSurface()) {
      m_Surface = vtkPolyData::SafeDownCast(mesh->GetMesh());
  }
}

//----------
// ShowData
//----------
//
void Centerlines::ShowData()
{
  vtkIdType numberOfPointArrays = m_Polydata->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of PointData arrays: " << numberOfPointArrays << std::endl;
  std::cout << "PointData arrays: " << std::endl;

  for(vtkIdType i = 0; i < numberOfPointArrays; i++) {
    int dataTypeID = m_Polydata->GetPointData()->GetArray(i)->GetDataType();  // float, double (11), etc.
    auto arrayName = std::string(m_Polydata->GetPointData()->GetArrayName(i));
    //std::cout << "Array " << i << ": " << arrayName << " (type: " << dataTypeID << ")" << std::endl;
 
    if (arrayName == "MaximumInscribedSphereRadius") { 
      std::cout << "Have MaximumInscribedSphereRadius data" << std::endl;
      m_RadiusData = vtkDoubleArray::SafeDownCast(m_Polydata->GetPointData()->GetArray(arrayName.c_str()));
    } 

    if (arrayName == "ParallelTransportNormals") { 
      std::cout << "Have ParallelTransportNormals data" << std::endl;
      m_NormalData = vtkDoubleArray::SafeDownCast(m_Polydata->GetPointData()->GetArray(arrayName.c_str()));
    }

    // Abscissa data measures the distances along the centerline.
    if (arrayName == "Abscissas") { 
      std::cout << "Have Abscissas data" << std::endl;
      m_AbscissaData = vtkDoubleArray::SafeDownCast(m_Polydata->GetPointData()->GetArray(arrayName.c_str()));
    }
  }

  // Set material IDs.
  m_MaterialID = 1;
  for (int i = 0; i < m_NumCenterLineVerts; i++) {
    m_CenterLineMaterialIDs.push_back(i);
    //centerLineMaterialIDs.push_back(materialID);
  } 
} 

//---------------------
// create_cell_locator
//---------------------
// Create a vtkCellLocator to find picked points in centerlines.
//
void Centerlines::create_cell_locator()
{
  m_CellLocator = vtkSmartPointer<vtkCellLocator>::New();
  m_CellLocator->SetDataSet(m_Polydata);
  m_CellLocator->BuildLocator();

  m_PointSet = vtkSmartPointer<vtkPolyData>::New();
  m_PointSet->SetPoints(m_Polydata->GetPoints());
}


//-------------
// locate_cell
//-------------
// Locate the given point in centerlines.
//
void Centerlines::locate_cell(double point[3], int& index, double& radius, double normal[3], double tangent[3])
{
  std::cout << std::endl;
  std::cout << "---------- Select Centerline Point ----------" << std::endl;
  std::cout << "Point: " << point[0] << " " << point[1] << " " << point[2] << std::endl;

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
  m_CellLocator->FindClosestPoint(point, closestPoint, cellId, subId, closestPointDist2);
  index = m_PointSet->FindPoint(point);
  std::cout << "Closest point: " << closestPoint[0] << " " << closestPoint[1] << " " << closestPoint[2] << std::endl;
  std::cout << "Distance to closest point: " << closestPointDist2 << std::endl;
  std::cout << "CellId: " << cellId << std::endl;
  std::cout << "Index: " << index << std::endl;

  if (m_CenterLineMaterialIDs.size() != 0) {
    std::cout << "Material ID: " << m_CenterLineMaterialIDs[index] << std::endl;
  }

  if (m_RadiusData) {
    radius = m_RadiusData->GetValue(index);
    std::cout << "Radius: " << radius << std::endl;
  }

  if (m_NormalData) {
    m_NormalData->GetTuple(index, normal);
    std::cout << "Normal: " << normal[0] << " " << normal[1] << " " << normal[2] << std::endl;
  }

  // Abscissas measure the distances along the centerline.
  if (m_AbscissaData) {
    auto distance = m_AbscissaData->GetValue(index);
    std::cout << "Distance: " << distance << std::endl;
  }

  // Compute tangent.
  //
  double p1[3], p2[3], v[3];
  m_Polydata->GetPoint(index, p1);
  m_Polydata->GetPoint(index+2, p2);
  vtkMath::Subtract(p2, p1,tangent);
  vtkMath::Normalize(tangent);
  std::cout << "Tangent " << tangent[0] << " " << tangent[1] << " " << tangent[2] << std::endl;
}

//------------------
// write_centerline
//------------------
//
void Centerlines::write_centerline()
{
  std::cout << "[write_centerline] " << std::endl;

  // Construct Get name of file to store material IDs.
  //
  size_t loc = m_FileName.find_last_of(".");
  std::string name;
  std::string ext; m_FileName.substr(loc, m_FileName.size() - loc);
  if (loc != std::string::npos) {
    name = m_FileName.substr(0, loc);
    ext  = m_FileName.substr(loc, m_FileName.size() - loc);
  } else {
    name = m_FileName;
    ext  = "";
  }
  std::string materialFileName = name + "_material" + ext;
  std::cout << "[write_centerline] Material file name " << materialFileName << std::endl;

  // Create new poly data.
  //
  vtkSmartPointer<vtkPolyData> newPolyData = vtkSmartPointer<vtkPolyData>::New();
  // Copy points.
  vtkSmartPointer<vtkPoints> newPoints = vtkSmartPointer<vtkPoints>::New();
  auto points = m_Polydata->GetPoints();
  for(vtkIdType i = 0; i < points->GetNumberOfPoints(); i++) {
    double p[3];
    points->GetPoint(i,p);
    newPoints->InsertNextPoint(p);
  }
  newPolyData->SetPoints(newPoints);
  // Copy cells.
  vtkSmartPointer<vtkCellArray> newCells = vtkSmartPointer<vtkCellArray>::New();
  for (vtkIdType i = 0; i < m_Polydata->GetNumberOfCells(); i++) {
    //std::cout << "[write_centerline] Cell " << i << std::endl;
    vtkCell* cell = m_Polydata->GetCell(i);
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
  std::cout << "Number of material data points: " << m_CenterLineMaterialIDs.size() << std::endl;

  // Set data to store.
  vtkSmartPointer<vtkIntArray> materialIDs = vtkSmartPointer<vtkIntArray>::New();
  materialIDs->SetName("MaterialIDs");
  materialIDs->SetNumberOfComponents(1);
  //materialIDs->SetNumberOfTuples(1);
  for (auto& id : m_CenterLineMaterialIDs) {
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
