
// This C++ program ia used to interactively 
//
// Usage:
//
//     slice-image <FileName>(.vti)
//
#include <iostream>
#include <string>

#include "Graphics.h"

//------
// main
//------

int main(int argc, char* argv[])
{
  if (argc < 1) {
    std::cout << "Usage: " << argv[0] << " <FileName>.{vti}" << std::endl;
    return EXIT_FAILURE;
  }

  // Read in VTK VTI file.
  //
  std::string fileName = argv[1];
  auto fileExt = fileName.substr(fileName.find_last_of(".") + 1);
  std::cout << "File extension: " << fileExt << std::endl;

  auto filePrefix = fileName.substr(0,fileName.find_last_of(".") - 1);
  std::cout << "File prefix: " << filePrefix << std::endl;

/*
  Mesh& mesh = CreateMesh(fileExt);
  mesh.ReadMesh(fileName);
  mesh.FindData();
*/


  // Create graphics interface.
  auto graphics = Graphics();
  //graphics.SetMesh(&mesh);
  //graphics.SetCenterlines(centerlines);

  graphics.Start();

  }

