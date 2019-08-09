
// This C++ program ia used to interactively extract simulation results at slice planes along vessel centerlines.
// Simulation results are read from VTK format (.vtp and .vtu) files created by the SimVascular svSolver and svPost programs.
// A file is read in and the data names for the simulation results data values contained in the file are printed. The finite element
// mesh is displyed and slices along a centerline can be selected using the mouse and keyboard.
//
// Usage:
//
//     slice-results <FileName>(.vtu | .vtp) <DataName>
//
#include <iostream>
#include <string>

#include "Graphics.h"
#include "Mesh.h"
#include "SurfaceMesh.h"
#include "Centerlines.h"

//------------
// CreateMesh
//------------
//
Mesh& CreateMesh(const std::string& meshType) 
{
  if (meshType == "vtp") {
    auto surf = new SurfaceMesh();
    return *surf;
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
  if (argc < 2) {
    std::cout << "Usage: " << argv[0] << " <FileName>.{vtu | vtp}" << "  <CenterlineFileName>.vtp " << std::endl;
    return EXIT_FAILURE;
  }

  // Read in VTK mesh file.
  //
  std::string fileName = argv[1];
  auto fileExt = fileName.substr(fileName.find_last_of(".") + 1);
  std::cout << "File extension: " << fileExt << std::endl;

  auto filePrefix = fileName.substr(0,fileName.find_last_of(".") - 1);
  std::cout << "File prefix: " << filePrefix << std::endl;

  Mesh& mesh = CreateMesh(fileExt);
  mesh.ReadMesh(fileName);
  mesh.FindData();

  // Read in VTK centerline file.
  //
  std::string clFileName = argv[2];
  auto centerlines = Centerlines();
  centerlines.ReadCenterlines(clFileName);
  centerlines.SetMesh(&mesh);

  // Create graphics interface.
  auto graphics = Graphics();
  graphics.SetMesh(&mesh);
  graphics.SetCenterlines(centerlines);

  if (argc == 4) {
    graphics.SetDataName(argv[3]);
  }

  // Add mesh and centerlines geometry to graphics.
  mesh.AddGeometry(graphics);
  mesh.SetGraphics(&graphics);
  centerlines.AddGeometry(graphics);

  graphics.Start();

  }

