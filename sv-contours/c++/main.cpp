
#include <vtkActor.h>
#include <vtkImageData.h>
#include <vtkImageDataGeometryFilter.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkPolyData.h>
#include <vtkPointData.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkSmartPointer.h>
#include <vtkXMLPolyDataWriter.h>
#include <vtkXMLImageDataWriter.h>
#include <vtkXMLImageDataReader.h>
#include <vtkXMLPolyDataReader.h>

int main ( int argc, char *argv[] )
{
  // Parse command line arguments
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " Filename(.vtp)" << std::endl;
    return EXIT_FAILURE;
  }

  std::string filename = argv[1];

  // Read surface data. 
  //
  vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
  reader->SetFileName(filename.c_str());
  reader->Update();
  vtkPolyData* polyData = NULL;
  polyData = reader->GetOutput();

  // Get bounds.
  //
  double bounds[6];
  polyData->GetBounds(bounds);
  double xmin = bounds[0]; double xmax = bounds[1]; double ymin = bounds[2];
  double ymax = bounds[3]; double zmin = bounds[4]; double zmax = bounds[5];
  std::cout << "xmin: " << xmin << "  xmax: " << xmax << std::endl;
  std::cout << "ymin: " << ymin << "  ymax: " << ymax << std::endl;
  std::cout << "zmin: " << zmin << "  zmax: " << zmax << std::endl;

  // Create surface graphics geometry.
  //
  vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  mapper->SetInputConnection(reader->GetOutputPort());
  mapper->ScalarVisibilityOff();
  vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  actor->GetProperty()->SetColor(1.0, 0.0, 0.0);
  actor->GetProperty()->SetRepresentationToWireframe();

  vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
  vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(1000,1000);

  // Add trackball interactor.
  //
  vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  renderWindowInteractor->SetRenderWindow(renderWindow);
  vtkSmartPointer<vtkInteractorStyleTrackballCamera> style = vtkSmartPointer<vtkInteractorStyleTrackballCamera>::New(); 
  renderWindowInteractor->SetInteractorStyle(style);

  renderer->AddActor(actor);
  renderer->SetBackground(0.8, .8, .8); 

  renderWindow->Render();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
