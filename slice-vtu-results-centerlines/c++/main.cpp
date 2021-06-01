
// This is a C++ program used to interactively extract simulation results at slice planes along vessel centerlines.
// Simulation results are read from VTK format (.vtu) files created by the SimVascular svSolver and svPost programs.
// The finite element mesh is displayed and slices along a centerline can be selected using the mouse.
//
// Usage:
//
//     slice-results results.vtu centerlines.vtp
//
#include <iostream>
#include <string>

#include "Graphics.h"
#include "Mesh.h"
#include "Centerlines.h"

//------
// main
//------
//
int main(int argc, char* argv[])
{
  if (argc < 2) {
    std::cout << "Usage: " << argv[0] << " Results file name (.vtu)" << "  centerlines file name (.vtp) " << std::endl;
    return EXIT_FAILURE;
  }

  // Read in VTK mesh file.
  //
  std::string file_name = argv[1];
  auto fileExt = file_name.substr(file_name.find_last_of(".") + 1);
  std::cout << "File extension: " << fileExt << std::endl;

  auto filePrefix = file_name.substr(0,file_name.find_last_of(".") - 1);
  std::cout << "File prefix: " << filePrefix << std::endl;

  // Read the volume results mesh.
  auto mesh = new Mesh();
  mesh->read_mesh(file_name);

  if (argc == 2) {
    return 0;
  }

  // Read in the centerline file.
  std::string cl_file_name = argv[2];
  auto centerlines = new Centerlines();
  centerlines->read_centerlines(cl_file_name);
  centerlines->mesh_ = mesh;

  // Create graphics interface.
  auto graphics = new Graphics();
  graphics->mesh_ = mesh;
  graphics->set_centerlines(centerlines);

  // Add mesh and centerlines geometry to graphics.
  mesh->graphics_ = graphics;
  //mesh->add_geometry();

  centerlines->graphics_ = graphics;
  centerlines->add_geometry();

  graphics->start();
  }

