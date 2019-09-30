
// This is an example of reading in an unstructured mesh. 
//
// Usage:
//
//     read-results <FileName>(.vtu | .vtp)
//
#include <iostream>
#include <string>

#include "Graphics.h"
#include "Mesh.h"
#include "SurfaceMesh.h"
#include "VolumeMesh.h"

//------------
// CreateMesh
//------------
//
Mesh& CreateMesh(const std::string& meshType) 
{
  if (meshType == "vtp") {
    auto surf = new SurfaceMesh();
    return *surf;
  } else if (meshType == "vtu") {
    auto volume = new VolumeMesh();
    return *volume;
  } else {
    auto msg = "Unknown extension '" + meshType + "'";
    std::cerr << msg << std::endl;
    exit(1);
  }

}

//------
// main
//------

int main(int argc, char* argv[])
{
  if (argc < 1) {
    std::cout << "Usage: " << argv[0] << " <FileName>.{vtu | vtp}" << std::endl;
    return EXIT_FAILURE;
  }

  // Read in VTK mesh file.
  //
  std::string fileName = argv[1];
  auto fileExt = fileName.substr(fileName.find_last_of(".") + 1);
  std::cout << "File extension: " << fileExt << std::endl;
  Mesh& mesh = CreateMesh(fileExt);
  mesh.ReadMesh(fileName);
  mesh.FindData();
  mesh.CheckNodeIDs();
  /* Experiment with removing mesh duplicate nodes.
  if (mesh.m_DupeNodeIDs.size() > 0) {
      mesh.FixMesh();
  }
  */

  // Create graphics interface.
  auto graphics = Graphics();
  graphics.SetMesh(&mesh);

  if (argc == 3) {
    graphics.SetDataName(argv[2]);
  }

  // Add mesh geometry to graphics.
  mesh.AddGeometry(graphics);

  graphics.ShowDuplicateCoords();

  graphics.Start();

  }

