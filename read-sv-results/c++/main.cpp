// Read SimVascular results from a .vtp or .vtu file. 
//
// Usage:
//
//     read-results <FileName>(.vtu | .vtp)
//
// The svSolver (svPost) writes surface mesh results as vtkPolyData rather
// than vtkUnstructuredGrid so the print functions must be duplicated for
// each mesh type.
//
#include <array>
#include <iostream>
#include <map>
#include <string>
#include <vtkDoubleArray.h>

#include <vtkCellData.h>
#include <vtkGenericCell.h>
#include <vtkGeometryFilter.h>
#include <vtkPointData.h>
#include <vtkPolyData.h>
#include <vtkUnstructuredGrid.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLUnstructuredGridReader.h>
#include <vtkXMLUnstructuredGridWriter.h>

//-----------
// PrintData
//-----------
// Print the mesh data.
//
void PrintData(vtkPolyData* polydata)
{ 
  std::cout << "---------- Mesh Data ----------" << std::endl;
  auto nodeIDs = vtkIntArray::SafeDownCast(polydata->GetPointData()->GetArray("GlobalNodeID"));
  auto numPoints = polydata->GetNumberOfPoints();
  vtkIdType numPointArrays = polydata->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of node data arrays: " << numPointArrays << std::endl;
  for(vtkIdType i = 0; i < numPointArrays; i++) {
    int type = polydata->GetPointData()->GetArray(i)->GetDataType();
    auto name = polydata->GetPointData()->GetArrayName(i);
    if (type == VTK_DOUBLE) {
      auto data = vtkDoubleArray::SafeDownCast(polydata->GetPointData()->GetArray(name));
      auto numComp = data->GetNumberOfComponents();
      std::cout << "Node data array: " << name << std::endl;
      std::cout << "  Number of components: " << numComp << std::endl;

      // Vectors.
      //
      if (numComp == 3) {
        std::map<int,std::array<double,3>> idValue;
        auto numVectors = data->GetNumberOfTuples();
        for (int j = 0; j < numPoints; j++) {
          auto id = nodeIDs->GetValue(j); 
          auto vx = data->GetComponent(j, 0);
          auto vy = data->GetComponent(j, 1);
          auto vz = data->GetComponent(j, 2);
          idValue[id] = {vx, vy, vz};
          //idValue[id][0] = vx;
          //idValue[id][1] = vy;
          //idValue[id][2] = vz;
          //std::cout << id << "  " << vx << "  " << vy << "  " << vz << std::endl;
        }
        for (auto const& entry : idValue) {
          std::cout << entry.first << "  " << entry.second[0] << "  " << entry.second[1] << "  " << entry.second[2] << std::endl;
        }

      // Scalars.
      //
      } else if (numComp == 1) {
        std::map<int,double> idValue;
        for (int j = 0; j < numPoints; j++) {
          auto id = nodeIDs->GetValue(j); 
          auto value = data->GetValue(j); 
          idValue[id] = value;
        }
        for (auto const& entry : idValue) {
          std::cout << entry.first << "  " << "  " << entry.second << std::endl;
        }
      }
    }
  }
}

//-----------
// PrintData
//-----------
// Print the mesh data.
//
void PrintData(vtkUnstructuredGrid* mesh)
{ 
  std::cout << "---------- Mesh Data ----------" << std::endl;
  auto pointIDs = vtkIntArray::SafeDownCast(mesh->GetPointData()->GetArray("GlobalNodeID"));
  auto numPoints = mesh->GetNumberOfPoints();
  vtkIdType numPointArrays = mesh->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of node data arrays: " << numPointArrays << std::endl;
  for(vtkIdType i = 0; i < numPointArrays; i++) {
    int type = mesh->GetPointData()->GetArray(i)->GetDataType();
    auto name = mesh->GetPointData()->GetArrayName(i);
    if (type == VTK_DOUBLE) {
      auto data = vtkDoubleArray::SafeDownCast(mesh->GetPointData()->GetArray(name));
      auto numComp = data->GetNumberOfComponents();
      std::cout << "Node data array: " << name << std::endl;

      // Vectors.
      //
      if (numComp == 3) {
        std::map<int,std::array<double,3>> idValue;
        auto numVectors = data->GetNumberOfTuples();
        for (int j = 0; j < numPoints; j++) {
          auto id = pointIDs->GetValue(j); 
          auto vx = data->GetComponent(j, 0);
          auto vy = data->GetComponent(j, 1);
          auto vz = data->GetComponent(j, 2);
          idValue[id] = {vx, vy, vz};
          //idValue[id][0] = vx;
          //idValue[id][1] = vy;
          //idValue[id][2] = vz;
          //std::cout << id << "  " << vx << "  " << vy << "  " << vz << std::endl;
        }
        for (auto const& entry : idValue) {
          std::cout << entry.first << "  " << entry.second[0] << "  " << entry.second[1] << "  " << entry.second[2] << std::endl;
        }

      // Scalars.
      //
      } else if (numComp == 1) {
        std::map<int,double> idValue;
        for (int j = 0; j < numPoints; j++) {
          auto id = pointIDs->GetValue(j); 
          auto value = data->GetValue(j); 
          idValue[id] = value;
        }
        for (auto const& entry : idValue) {
          std::cout << entry.first << "  " << "  " << entry.second << std::endl;
        }
      }
    }
  }
}

//-----------
// PrintMesh
//-----------
// Print the mesh coordinates and element connectivity.
//
void PrintMesh(vtkUnstructuredGrid* mesh)
{
  const int NODES_PER_ELEM = 4;
  auto pointIDs = vtkIntArray::SafeDownCast(mesh->GetPointData()->GetArray("GlobalNodeID"));
  auto numPoints = mesh->GetNumberOfPoints();
  std::cout << "---------- Mesh ----------" << std::endl;
  std::cout << "Number of coordinates: " << numPoints << std::endl;
  std::cout << "Coordinates: " << std::endl;
  std::map<int,std::array<double,3>> idCoords;

  // Sort coordinates by node ID.
  //
  for (int i = 0; i < numPoints; i++) {
    double pt[3]; 
    auto id = pointIDs->GetValue(i); 
    mesh->GetPoint(i, pt); 
    idCoords[id] = {pt[0], pt[1], pt[2]};
  }
  for (auto const& entry : idCoords) {
    std::cout << entry.first << "  " << entry.second[0] << "  " << entry.second[1] << "  " << entry.second[2] << std::endl;
  }

  // Sort element IDs.
  //
  auto numCells = mesh->GetNumberOfCells();
  //auto numCells = polydata->GetNumberOfCells();
  auto elemIDs = vtkIntArray::SafeDownCast(mesh->GetCellData()->GetArray("GlobalElementID"));
  vtkGenericCell* cell = vtkGenericCell::New();
  std::map<int,std::array<int,NODES_PER_ELEM>> idElems;

  for (int i = 0; i < numCells; i++) {
    mesh->GetCell(i, cell);
    auto elemID = elemIDs->GetValue(i); 
    auto numElemNodes = cell->GetNumberOfPoints();
    for (vtkIdType pointInd = 0; pointInd < cell->GetNumberOfPoints(); ++pointInd) {
      auto k = cell->PointIds->GetId(pointInd);
      auto id = pointIDs->GetValue(k); 
      idElems[elemID][pointInd] = id;
    }
  }

  std::cout << "Number of elements: " << numCells << std::endl;
  std::cout << "Element connectivity: " << std::endl;
  for (auto const& entry : idElems) { 
    std::cout << entry.first << "  "; 
    for (int j = 0; j < NODES_PER_ELEM; ++j) {
        std::cout << entry.second[j] << "  "; 
    }
    std::cout << std::endl;
  }

 // Write just the mesh.
 /*
 std::string fileName = "mesh.vtu";
 vtkSmartPointer<vtkXMLUnstructuredGridWriter> writer = vtkSmartPointer<vtkXMLUnstructuredGridWriter>::New();
 writer->SetFileName(fileName.c_str());
 writer->SetInputData(mesh);
 writer->Update();
 */

}

//-----------
// PrintMesh
//-----------
// Print the mesh coordinates and element connectivity.
//
void PrintMesh(vtkPolyData* polydata)
{ 
  const int NODES_PER_ELEM = 3;
  auto nodeIDs = vtkIntArray::SafeDownCast(polydata->GetPointData()->GetArray("GlobalNodeID"));
  auto numIDs = nodeIDs->GetNumberOfValues();
  auto numPoints = polydata->GetNumberOfPoints();

  std::cout << "---------- Mesh ----------" << std::endl;
  /*
  std::cout << "Global Node IDs: " << std::endl;
  std::cout << "  Number of IDs: " << numIDs << std::endl;
  std::cout << "  IDs: " ;
  for (int i = 0; i < numIDs; i++) {
    auto id = nodeIDs->GetValue(i);
    std::cout << id << " ";
  }
  std::cout << std::endl;
  */

  std::cout << "Number of coordinates: " << numPoints << std::endl;
  std::cout << "Coordinates: " << std::endl;
  std::map<int,std::array<double,3>> idCoords;

  // Sort coordinates by node ID.
  //
  for (int i = 0; i < numPoints; i++) {
    double pt[3]; 
    auto id = nodeIDs->GetValue(i); 
    polydata->GetPoint(i, pt); 
    idCoords[id] = {pt[0], pt[1], pt[2]};
  }
  int n = 1;
  for (auto const& entry : idCoords) {
    std::cout << n << " " << entry.first << "  " << entry.second[0] << "  " << entry.second[1] << "  " << entry.second[2] << std::endl;
    n += 1; 
  }

  // Sort element IDs.
  //
  auto numCells = polydata->GetNumberOfPolys();
  //auto numCells = polydata->GetNumberOfCells();
  auto elemIDs = vtkIntArray::SafeDownCast(polydata->GetCellData()->GetArray("GlobalElementID"));
  vtkGenericCell* cell = vtkGenericCell::New();
  std::map<int,std::array<int,NODES_PER_ELEM>> idElems;
  std::map<int,std::array<int,NODES_PER_ELEM>> dupeElems;
  int numDupeIDs = 0;

  for (int i = 0; i < numCells; i++) {
    polydata->GetCell(i, cell);
    auto elemID = elemIDs->GetValue(i); 
    auto numElemNodes = cell->GetNumberOfPoints();
    bool dupe = false;
    if (idElems.find(elemID) != idElems.end()) {
      //std::cout << "WARNING: Duplicate element ID: " << elemID << std::endl;
      dupe = true;
      numDupeIDs += 1;
    } 
    for (vtkIdType pointInd = 0; pointInd < cell->GetNumberOfPoints(); ++pointInd) {
      auto k = cell->PointIds->GetId(pointInd);
      auto id = nodeIDs->GetValue(k); 
      if (dupe) {
        dupeElems[elemID][pointInd] = id;
      } else {
        idElems[elemID][pointInd] = id;
      }
    }
  }

  std::cout << "Number of elements: " << numCells << std::endl;
  std::cout << "Element connectivity: " << std::endl;
  n = 1;
  for (auto const& entry : idElems) { 
    std::cout << n << " " << entry.first << "  "; 
    for (int j = 0; j < NODES_PER_ELEM; ++j) {
        std::cout << entry.second[j] << "  "; 
    }
    n += 1;
    std::cout << std::endl;
  }

  std::cout << "WARNING: " << numDupeIDs << " Duplicate element IDs" << std::endl;
  std::cout << "Duplicate element connectivity: " << std::endl;
  n = 1;
  for (auto const& entry : dupeElems) { 
    std::cout << n << " " << entry.first << "  "; 
    for (int j = 0; j < NODES_PER_ELEM; ++j) {
        std::cout << entry.second[j] << "  "; 
    }
    n += 1;
    std::cout << std::endl;
  }
}

//----------------
// PrintDataNames
//----------------
//
void PrintDataNames(vtkPolyData* polydata)
{ 
  vtkIdType numPointArrays = polydata->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of node data arrays: " << numPointArrays << std::endl;
  std::cout << "Node data arrays: " << std::endl;
  for(vtkIdType i = 0; i < numPointArrays; i++) {
    int type = polydata->GetPointData()->GetArray(i)->GetDataType();
    auto name = polydata->GetPointData()->GetArrayName(i);
    std::cout << "   " << i << ": " << name << "   type: " << vtkImageScalarTypeNameMacro(type) << std::endl;
  }           

  vtkIdType numCellArrays = polydata->GetCellData()->GetNumberOfArrays();
  std::cout << "Number of element data arrays: " << numCellArrays << std::endl;
  std::cout << "Element data arrays: " << std::endl;
  for (vtkIdType i = 0; i < numCellArrays; i++) {
    int type = polydata->GetCellData()->GetArray(i)->GetDataType();
    auto name = polydata->GetCellData()->GetArrayName(i);
    std::cout << "   " << i << ": " << name << "   type: " << vtkImageScalarTypeNameMacro(type) << std::endl;
  }           
}

//----------------
// PrintDataNames
//----------------
//
void PrintDataNames(vtkUnstructuredGrid* mesh)
{ 
  vtkIdType numPointArrays = mesh->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of node data arrays: " << numPointArrays << std::endl;
  std::cout << "Node data arrays: " << std::endl;
  for(vtkIdType i = 0; i < numPointArrays; i++) {
    int type = mesh->GetPointData()->GetArray(i)->GetDataType();
    auto name = mesh->GetPointData()->GetArrayName(i);
    std::cout << "   " << i << ": " << name << "   type: " << vtkImageScalarTypeNameMacro(type) << std::endl;
  }

  vtkIdType numCellArrays = mesh->GetCellData()->GetNumberOfArrays();
  std::cout << "Number of element data arrays: " << numCellArrays << std::endl;
  std::cout << "Element data arrays: " << std::endl;
  for (vtkIdType i = 0; i < numCellArrays; i++) {
    int type = mesh->GetCellData()->GetArray(i)->GetDataType();
    auto name = mesh->GetCellData()->GetArrayName(i);
    std::cout << "   " << i << ": " << name << "   type: " << vtkImageScalarTypeNameMacro(type) << std::endl;
  }
}

//------
// main
//------
//
int main(int argc, char* argv[])
{
  if(argc != 2) {
    std::cout << "Usage: " << argv[0] << " <FileName>.{vtu | vtp}" << std::endl;
    return EXIT_FAILURE;
  }

  vtkSmartPointer<vtkPolyData> polydataMesh;
  vtkSmartPointer<vtkUnstructuredGrid> unstructuredMesh;

  // Read in VTK mesh file.
  //
  std::string fileName = argv[1];
  auto fileExt = fileName.substr(fileName.find_last_of(".") + 1);
  std::cout << "File extension: " << fileExt << std::endl;

  if (fileExt == "vtp") {
    vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
    reader->SetFileName(fileName.c_str());
    reader->Update();
    polydataMesh = vtkSmartPointer<vtkPolyData>::New();
    polydataMesh->DeepCopy(reader->GetOutput());
    vtkIdType numPoints = polydataMesh->GetNumberOfPoints();
    vtkIdType numPolys = polydataMesh->GetNumberOfPolys();
    std::cout << "Read polydata (.vtp) file: " << fileName << std::endl;
    std::cout << "  Number of nodes: " << numPoints << std::endl;
    std::cout << "  Number of elements: " << numPolys << std::endl;
    PrintDataNames(polydataMesh);
    PrintMesh(polydataMesh);
    PrintData(polydataMesh);

  } else if (fileExt == "vtu") {
    vtkSmartPointer<vtkXMLUnstructuredGridReader> reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
    reader->SetFileName(fileName.c_str());
    reader->Update();

    vtkSmartPointer<vtkGeometryFilter> geometryFilter = vtkSmartPointer<vtkGeometryFilter>::New();
    geometryFilter->SetInputData(reader->GetOutput());
    geometryFilter->Update();
    vtkPolyData* meshPolyData = geometryFilter->GetOutput();

    unstructuredMesh = vtkSmartPointer<vtkUnstructuredGrid>::New();
    unstructuredMesh->DeepCopy(reader->GetOutput());
    vtkIdType numPoints = unstructuredMesh->GetNumberOfPoints();
    vtkIdType numCells = unstructuredMesh->GetNumberOfCells();
    std::cout << "Read unstructured mesh (.vtu) file: " << fileName << std::endl;
    std::cout << "  Number of nodes: " << numPoints << std::endl;
    std::cout << "  Number of elements: " << numCells << std::endl;
    PrintDataNames(unstructuredMesh);
    PrintMesh(unstructuredMesh);
    PrintData(unstructuredMesh);
  }
}

