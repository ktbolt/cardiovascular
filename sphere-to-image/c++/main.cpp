
// Convert a sphere into an image.

#include <vtkImageData.h>
#include <vtkImageDataGeometryFilter.h>
#include <vtkMarchingCubes.h>
#include <vtkSphereSource.h>
#include <vtkVoxelModeller.h>

#include <vtkActor.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkPoints.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkVertexGlyphFilter.h>

#include <vtkXMLImageDataReader.h>
#include <vtkXMLImageDataWriter.h>

int main ( int argc, char *argv[] )
{

  // Set image dimentions.
  int idim = 100;
  int jdim = 100;
  int kdim = 100;
  double icx = (idim - 1) / 2.0;
  double icy = (jdim - 1) / 2.0;
  double icz = (kdim - 1) / 2.0;
  std::cout << "icx: " << icx << "  icy: " << icy << "  icz: " << icz << std::endl;
  double radius = icx / 4.0;

  // Create image data and points.
  //
  vtkSmartPointer<vtkPoints> points = vtkSmartPointer<vtkPoints>::New();
  vtkSmartPointer<vtkImageData> imageData = vtkSmartPointer<vtkImageData>::New();
  imageData->SetDimensions(idim, jdim, kdim);
  imageData->AllocateScalars(VTK_DOUBLE, 1);
  int* dims = imageData->GetDimensions();
  std::cout << "image dims[0]:" << dims[0] << "  dims[1]:" << dims[1] << "  dims[2]:" << dims[2] << std::endl;

  // Fill image data with sphere.
  //
  int n = 0;
  double dx = 1.0, dy = 1.0, dz = 1.0;
  auto z = 0.0;
  for (int k = 0; k < dims[2]; k++) {
    auto y = 0.0;
    for (int j = 0; j < dims[1]; j++) {
      auto x = 0.0;
      for (int i = 0; i < dims[0]; i++) {
        double* pixel = static_cast<double*>(imageData->GetScalarPointer(i,j,k));
        auto r = (x-icx)*(x-icx) + (y-icy)*(y-icy) + (z-icz)*(z-icz);
        if (r < radius*radius) {
          pixel[0] = 1.0;
          //pixel[0] = radius*radius - r;
          //std::cout << "radius*radius - r: " << radius*radius - r << std::endl; 
          n += 1;
          points->InsertNextPoint (x, y, z);
        } else {
          pixel[0] = 0.0;
        }
       
        x += dx;
      }
    y += dy;
    }
  z += dz;
  }
  std::cout << "number of points: " << idim*jdim*kdim << ::endl;
  std::cout << "number of points added: " << n << std::endl;

  // Write image.
  //
  std::string image_file_name = "sphere.vti";
  vtkSmartPointer<vtkXMLImageDataWriter> image_writer = vtkSmartPointer<vtkXMLImageDataWriter>::New();
  image_writer->SetFileName(image_file_name.c_str());
  image_writer->SetInputData(imageData);
  image_writer->Write();

  // Create polydata for points.
  vtkSmartPointer<vtkPolyData> pointsPolydata = vtkSmartPointer<vtkPolyData>::New();
  pointsPolydata->SetPoints(points);
  vtkSmartPointer<vtkVertexGlyphFilter> vertexFilter = vtkSmartPointer<vtkVertexGlyphFilter>::New();
  vertexFilter->SetInputData(pointsPolydata);
  vertexFilter->Update();
  vtkSmartPointer<vtkPolyData> polydata = vtkSmartPointer<vtkPolyData>::New();
  polydata->ShallowCopy(vertexFilter->GetOutput());
  vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  mapper->SetInputData(polydata);
  vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  actor->GetProperty()->SetPointSize(5);

  // Create renderer. 
  //
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

