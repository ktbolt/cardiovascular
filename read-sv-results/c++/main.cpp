// Read SimVascular results from a .vtp or .vtu file. 
//
// Usage:
//
//     read-results <FileName>(.vtu | .vtp)
//
#include <iostream>
#include <string>
#include <vtkDoubleArray.h>

#include <vtkGenericCell.h>
#include <vtkPointData.h>
#include <vtkPolyData.h>
#include <vtkUnstructuredGrid.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLUnstructuredGridReader.h>

//-----------
// PrintData
//-----------
//
void PrintData(vtkPolyData* polydata)
{ 
  std::cout << "---------- Mesh Data ----------" << std::endl;
  auto pointIDs = vtkIntArray::SafeDownCast(polydata->GetPointData()->GetArray("GlobalNodeID"));
  auto numPoints = polydata->GetNumberOfPoints();
  vtkIdType numPointArrays = polydata->GetPointData()->GetNumberOfArrays();
  std::cout << "Number of point data arrays: " << numPointArrays << std::endl;
  for(vtkIdType i = 0; i < numPointArrays; i++) {
    int type = polydata->GetPointData()->GetArray(i)->GetDataType();
    auto name = polydata->GetPointData()->GetArrayName(i);
    if (type == VTK_DOUBLE) {
        auto data = vtkDoubleArray::SafeDownCast(polydata->GetPointData()->GetArray(name));
        auto numComp = data->GetNumberOfComponents();
        std::cout << "Point data array: " << name << std::endl;
        if (numComp == 3) {
          auto numVectors = data->GetNumberOfTuples();
          for (int j = 0; j < numPoints; j++) {
            auto id = pointIDs->GetValue(j); 
            auto vx = data->GetComponent(j, 0);
            auto vy = data->GetComponent(j, 1);
            auto vz = data->GetComponent(j, 2);
            std::cout << j << ": " << id << "  " << vx << "  " << vy << "  " << vz << std::endl;
          }
        } else if (numComp == 1) {
          for (int j = 0; j < numPoints; j++) {
            auto id = pointIDs->GetValue(j); 
            auto value = data->GetValue(j); 
            std::cout << j << ": " << id << "  " << value << std::endl;
        }
      }
    }
  }

}

//-----------
// PrintMesh
//-----------
//
void PrintMesh(vtkPolyData* polydata)
{ 
  auto pointIDs = vtkIntArray::SafeDownCast(polydata->GetPointData()->GetArray("GlobalNodeID"));
  auto numPoints = polydata->GetNumberOfPoints();
  std::cout << "---------- Mesh ----------" << std::endl;
  std::cout << "Number of coordinates: " << numPoints << std::endl;
  std::cout << "Coordinates: " << std::endl;

  for (int i = 0; i < numPoints; i++) {
    double pt[3]; 
    auto id = pointIDs->GetValue(i); 
    polydata->GetPoint(i, pt); 
    std::cout << i << ": " << id << "  " << pt[0] << "  " << pt[1] << "   " << pt[2]  << std::endl;
  }

  auto numCells = polydata->GetNumberOfCells();
  std::cout << "Number of elements: " << numCells << std::endl;
  std::cout << "Element connectivity: " << std::endl;
  vtkGenericCell* cell = vtkGenericCell::New();

  for (int i = 0; i < numCells; i++) {
    polydata->GetCell(i, cell);
    std::cout << i << ": "; 
    for (vtkIdType pointInd = 0; pointInd < cell->GetNumberOfPoints(); ++pointInd) {
      auto k = cell->PointIds->GetId(pointInd);
      auto id = pointIDs->GetValue(k); 
      std::cout << id << " ";
    }
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
  std::cout << "Number of point data arrays: " << numPointArrays << std::endl;
  std::cout << "Point data arrays: " << std::endl;
  for(vtkIdType i = 0; i < numPointArrays; i++) {
    int type = polydata->GetPointData()->GetArray(i)->GetDataType();
    auto name = polydata->GetPointData()->GetArrayName(i);
    std::cout << "   " << i << ": " << name << "   type: " << vtkImageScalarTypeNameMacro(type) << std::endl;
  }           
}

//------
// main
//------

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
    std::cout << "  Number of points: " << numPoints << std::endl;
    std::cout << "  Number of polygons: " << numPolys << std::endl;
    PrintDataNames(polydataMesh);
    PrintMesh(polydataMesh);
    PrintData(polydataMesh);

  } else if (fileExt == "vtu") {
    vtkSmartPointer<vtkXMLUnstructuredGridReader> reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
    reader->SetFileName(fileName.c_str());
    reader->Update();

    unstructuredMesh = vtkSmartPointer<vtkUnstructuredGrid>::New();
    unstructuredMesh->DeepCopy(reader->GetOutput());
    vtkIdType numPoints = unstructuredMesh->GetNumberOfPoints();
    vtkIdType numCells = unstructuredMesh->GetNumberOfCells();
    std::cout << "Read unstructured mesh (.vtu) file: " << fileName << std::endl;
    std::cout << "  Number of points: " << numPoints << std::endl;
    std::cout << "  Number of elements: " << numCells << std::endl;
  }



}

