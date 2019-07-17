// Read SimVascular results from a .vtp or .vtu file and extract results by face IDs. 
//
// Usage:
//
//     extract-faceid-results mesh-complete.exterior.vtp <FileName>(.vtu | .vtp)
//
#include <array>
#include <iostream>
#include <map>
#include <string>
#include <vtkDoubleArray.h>

#include <vtkCellData.h>
#include <vtkCleanPolyData.h>
#include <vtkGenericCell.h>
#include <vtkGeometryFilter.h>
#include <vtkIntArray.h>
#include <vtkPointData.h>
#include <vtkPolyData.h>
#include <vtkTriangle.h>
#include <vtkUnstructuredGrid.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLPolyDataWriter.h>
#include <vtkXMLUnstructuredGridReader.h>

class Face {
  public:
    int faceID;
    std::vector<int> elemIDs;
};

//-----------------
// CreateFaceIdMap
//-----------------
//
void CreateFaceIdMap(vtkPolyData* polydata, vtkPolyData* resultsPolydataMesh)
{ 
  std::cout << "---------- Exterior Mesh Data ----------" << std::endl;
  auto nodeIDs = vtkIntArray::SafeDownCast(polydata->GetPointData()->GetArray("GlobalNodeID"));
  auto numPoints = polydata->GetNumberOfPoints();
  auto numCells = polydata->GetNumberOfCells();
  auto elemIDs = vtkIntArray::SafeDownCast(polydata->GetCellData()->GetArray("GlobalElementID"));
  std::cout << "Number of nodes: " << numPoints << std::endl;
  std::cout << "Number of elements: " << numCells << std::endl;
  // 
  auto faceIDs = vtkIntArray::SafeDownCast(polydata->GetCellData()->GetArray("ModelFaceID"));
  if (faceIDs == nullptr) {
    std::cout << "**** ERROR: No ModelFaceID data found in exterior mesh." << std::endl;
    exit(1);
  } 

  // Create a map of faceIDs to element lists.
  //
  std::map<int,std::vector<int>> faceElemMap;
  for (int i = 0; i < numCells; i++) {
    auto faceID = faceIDs->GetValue(i);
    faceElemMap[faceID].push_back(i);
  }

  std::cout << "Number of faces: " << faceElemMap.size() << std::endl;
  std::cout << "Create face surface meshes ... " << std::endl;
  vtkGenericCell* cell = vtkGenericCell::New();

  for (auto const& face : faceElemMap) {
    auto faceID = face.first;
    std::cout << ">>> Face: " << faceID << std::endl;
    auto elems = face.second;
    double pt[3];
    std::map<int,int> nodeIDMap;
    vtkSmartPointer<vtkIntArray> faceElemIDs = vtkSmartPointer<vtkIntArray>::New();
    faceElemIDs->SetName("GlobalElementID");
    faceElemIDs->SetNumberOfTuples(elems.size());
    int numNodeIDs = 0;
    int numElemIDs = 0;
    int nodeID;
    std::cout << "Number of elements: " << elems.size() << std::endl;
    vtkSmartPointer<vtkPoints> points = vtkSmartPointer<vtkPoints>::New();
    vtkSmartPointer<vtkCellArray> triangles = vtkSmartPointer<vtkCellArray>::New();

    for (auto const& elemIndex : elems) {
      auto elemID = elemIDs->GetValue(elemIndex);
      //std::cout << "ElemID: " << elemID << std::endl;
      polydata->GetCell(elemIndex, cell);
      auto numElemNodes = cell->GetNumberOfPoints();
      vtkSmartPointer<vtkTriangle> triangle = vtkSmartPointer<vtkTriangle>::New();
      for (int i = 0; i < numElemNodes; i++) {
        auto k = cell->PointIds->GetId(i);
        auto id = nodeIDs->GetValue(k);
        if (nodeIDMap.count(id)) {
          nodeID = nodeIDMap[id];
        } else {
          polydata->GetPoint(k, pt);
          points->InsertNextPoint(pt[0], pt[1], pt[2]);
          nodeIDMap[id] = numNodeIDs;
          nodeID = numNodeIDs; 
          numNodeIDs += 1; 
        }
        triangle->GetPointIds()->SetId(i, nodeID);
      }

      faceElemIDs->SetValue(numElemIDs, elemID);
      triangles->InsertNextCell(triangle);
      numElemIDs += 1;
    }

    // Create polydata triangle mesh.
    vtkSmartPointer<vtkPolyData> facePolydata = vtkSmartPointer<vtkPolyData>::New();
    facePolydata->SetPoints(points);
    facePolydata->SetPolys(triangles);
    std::cout << "Number of nodes: " << numNodeIDs << std::endl;

    // Add node and element IDs.
    vtkSmartPointer<vtkIntArray> faceNodeIDs = vtkSmartPointer<vtkIntArray>::New();
    faceNodeIDs->SetName("GlobalNodeID");
    faceNodeIDs->SetNumberOfTuples(nodeIDMap.size());
    for (auto const& node : nodeIDMap) {
      faceNodeIDs->SetValue(node.second, node.first);
    }
    facePolydata->GetPointData()->AddArray(faceNodeIDs);
    facePolydata->GetCellData()->AddArray(faceElemIDs);

    // Write the polydata.
    vtkSmartPointer<vtkXMLPolyDataWriter> writer = vtkSmartPointer<vtkXMLPolyDataWriter>::New();
    std::string fileName = "face" + std::to_string(faceID) + ".vtp";
    writer->SetFileName(fileName.c_str());
    writer->SetInputData(facePolydata);
    writer->Write();
  }

  std::cout << "Done." << std::endl;
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
  if (argc != 3) {
    std::cout << "Usage: " << argv[0] << " mesh-complete.exterior.vtp  <FileName>.{vtu | vtp}" << std::endl;
    return EXIT_FAILURE;
  }

  vtkSmartPointer<vtkPolyData> polydataMesh;
  vtkSmartPointer<vtkUnstructuredGrid> unstructuredMesh;

  // Read exterior mesh.
  //
  std::string extFileName = argv[1];
  auto extFileExt = extFileName.substr(extFileName.find_last_of(".") + 1);
  //std::cout << "Exterior mesh file extension: " << extFileExt << std::endl;
  vtkSmartPointer<vtkXMLPolyDataReader> extReader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  extReader->SetFileName(extFileName.c_str());
  extReader->Update();
  vtkSmartPointer<vtkPolyData> extPolydataMesh = vtkSmartPointer<vtkPolyData>::New();
  extPolydataMesh->DeepCopy(extReader->GetOutput());
  std::cout << "Read exterior mesh:" << std::endl;
  std::cout << "  Number of nodes: " << extPolydataMesh->GetNumberOfPoints() << std::endl;
  std::cout << "  Number of elements: " << extPolydataMesh->GetNumberOfPolys() << std::endl;

  // Read in SV results VTK mesh file.
  //
  std::string fileName = argv[2];
  auto fileExt = fileName.substr(fileName.find_last_of(".") + 1);
  //std::cout << "File extension: " << fileExt << std::endl;

  if (fileExt == "vtp") {
    // Read results mesh.
    //
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
    CreateFaceIdMap(extPolydataMesh, polydataMesh);

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
  }
}

