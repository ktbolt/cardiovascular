
// This script reads in an image from a VTI file, resets its origin and writes out a new image to new-origin.vti.

#include <vtkImageData.h>
#include <vtkImageDataGeometryFilter.h>
#include <vtkXMLImageDataReader.h>
#include <vtkXMLImageDataWriter.h>

int main ( int argc, char *argv[] )
{
  // Read image.
  auto image_file_name = argv[1];
  vtkSmartPointer<vtkXMLImageDataReader> image_reader = vtkSmartPointer<vtkXMLImageDataReader>::New();
  image_reader->SetFileName(image_file_name);
  image_reader->Update();
  auto image_data = image_reader->GetOutput();

  double origin[3];
  image_data->GetOrigin(origin);
  std::cout << "Origin: " << origin[0] << "  " << origin[1] << "  " << origin[2] << std::endl;

  //vtkSmartPointer<vtkXMLImageDataWriter> image_writer = vtkSmartPointer<vtkXMLImageDataWriter>::New();
  //image_writer->SetFileName("set-origin-image.vti");
  //image_writer->SetInputData(imageData);
  //image_writer->Write();

  return EXIT_SUCCESS;

}

