
#include <vtkDICOMImageReader.h>
#include <vtkImageData.h>
#include <vtkSmartPointer.h>
#include <vtkXMLImageDataWriter.h>

int main ( int argc, char *argv[] )
{
  // Parse command line arguments
  if(argc != 2) {
    std::cerr << "Usage: " << argv[0] << " DICOM directory " << std::endl;
    return EXIT_FAILURE;
  }

  std::string dicomDir = argv[1];

  // Read all the DICOM files in the specified directory. 
  vtkSmartPointer<vtkDICOMImageReader> reader = vtkSmartPointer<vtkDICOMImageReader>::New(); 
  reader->SetDirectoryName(dicomDir.c_str()); 
  reader->Update(); 

  // Write vti.
  vtkSmartPointer<vtkXMLImageDataWriter> writer = vtkSmartPointer<vtkXMLImageDataWriter>::New(); 
  writer->SetFileName("volume.vti"); 
  writer->SetInputData(reader->GetOutput()); 
  writer->Write(); 
  }

