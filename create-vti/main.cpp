
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
  if(argc != 2) {
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

  // Get points bounds.
  //
  double bounds[6];
  polyData->GetBounds(bounds);
  double xmin = bounds[0]; double xmax = bounds[1]; double ymin = bounds[2];
  double ymax = bounds[3]; double zmin = bounds[4]; double zmax = bounds[5];
  double dx = xmax - xmin; double dy = ymax - ymin; double dz = zmax - zmin;
  double cx = xmin + dx / 2.0;    double cy = ymin + dy / 2.0;    double cz = zmin + dz / 2.0;
  std::cout << "xmin: " << xmin << "  xmax: " << xmax << std::endl;
  std::cout << "ymin: " << ymin << "  ymax: " << ymax << std::endl;
  std::cout << "zmin: " << zmin << "  zmax: " << zmax << std::endl;
  std::cout << "dx: " << dx << "  dy: " << dy << "  dz: " << dz << std::endl;
  std::cout << "orig  cx: " << cx << "  cy: " << cy << "  cz: " << cz << std::endl;

  double scale = 1.0;

  if ((dx < 1.0) || (dy < 1.0) || (dz < 1.0)) {
    scale = 10.0;
  }
  /*
  dx *= scale;
  dy *= scale;
  dz *= scale;
  */
  std::cout << "scale: " << scale << std::endl;

  // Translate surface.
  //
  double tx, ty, tz;
  tx = -xmin;
  ty = -ymin;
  tz = -zmin;

  vtkSmartPointer<vtkPoints> points = vtkSmartPointer<vtkPoints>::New();
  points->ShallowCopy(polyData->GetPoints());

  for(vtkIdType i = 0; i < polyData->GetNumberOfPoints(); i++) {
    double *p = points->GetPoint(i); 
    p[0] = p[0] + tx;
    p[1] = p[1] + ty;
    p[2] = p[2] + tz;
    points->SetPoint(i,p);
  }

  points->Modified(); 
  polyData->Modified();
  polyData->GetBounds(bounds);

  xmin = bounds[0]; xmax = bounds[1]; ymin = bounds[2];
  ymax = bounds[3]; zmin = bounds[4]; zmax = bounds[5];
  dx = xmax - xmin; dy = ymax - ymin; dz = zmax - zmin;
  dx *= scale;
  dy *= scale;
  dz *= scale;
  cx = xmin + dx / 2.0;    cy = ymin + dy / 2.0;    cz = zmin + dz / 2.0;
  if (dx == 2.0) dx = 3.0;
  if (dy == 2.0) dy = 3.0;
  if (dz == 2.0) dz = 3.0;
  std::cout << "trans xmin: " << xmin << "  xmax: " << xmax << std::endl;
  std::cout << "trans ymin: " << ymin << "  ymax: " << ymax << std::endl;
  std::cout << "trans zmin: " << zmin << "  zmax: " << zmax << std::endl;
  std::cout << "trans: cx " << cx << "  cy " << cy << "  cz " << cz << std::endl;
  std::cout << "trans: dx " << dx << "  dy " << dy << "  dz " << dz << std::endl;

  // Write translated surface.
  //
  size_t loc = filename.find_last_of(".");
  std::string name;
  std::string ext; filename.substr(loc, filename.size() - loc);
  if (loc != std::string::npos) {
    name = filename.substr(0, loc);
    ext  = filename.substr(loc, filename.size() - loc);
  } else {
    name = filename;
    ext  = "";
  }
  std::string trans_filename = name + "_trans" + ext; 
  vtkSmartPointer<vtkXMLPolyDataWriter> writer = vtkSmartPointer<vtkXMLPolyDataWriter>::New();
  writer->SetFileName(trans_filename.c_str());
  writer->SetInputData(polyData);
  writer->Write();

  // Create image data.
  //
  vtkSmartPointer<vtkImageData> imageData = vtkSmartPointer<vtkImageData>::New();
  int idx = int(dx);
  int idy = int(dy);
  int idz = int(dz);
  std::cout << "image idx: " << idx << "  idy: " << idy << "  idz: " << idz << std::endl;
  imageData->SetDimensions(idx,idy,idz);
  imageData->AllocateScalars(VTK_DOUBLE, 1);
  int* dims = imageData->GetDimensions();
  std::cout << "image dims[0]:" << dims[0] << "  dims[1]:" << dims[1] << "  dims[2]:" << dims[2] << std::endl;

  // Fill every entry of the image data with "2.0"
  for (int z = 0; z < dims[2]; z++) {
    for (int y = 0; y < dims[1]; y++) {
      for (int x = 0; x < dims[0]; x++) {
        double* pixel = static_cast<double*>(imageData->GetScalarPointer(x,y,z));
        pixel[0] = 2.0;
      }
    }
  }

  std::string image_file_name = name + ".vti";
  vtkSmartPointer<vtkXMLImageDataWriter> image_writer = vtkSmartPointer<vtkXMLImageDataWriter>::New();
  image_writer->SetFileName(image_file_name.c_str());
  image_writer->SetInputData(imageData);
  image_writer->Write();

  // Convert the image to a polydata
  //
  vtkSmartPointer<vtkXMLImageDataReader> ireader = vtkSmartPointer<vtkXMLImageDataReader>::New();
  ireader->SetFileName(image_file_name.c_str());
  ireader->Update();
  //
  vtkSmartPointer<vtkImageDataGeometryFilter> imageDataGeometryFilter = vtkSmartPointer<vtkImageDataGeometryFilter>::New();
  imageDataGeometryFilter->SetInputConnection(ireader->GetOutputPort());
  imageDataGeometryFilter->Update();
  vtkSmartPointer<vtkPolyDataMapper> imapper = vtkSmartPointer<vtkPolyDataMapper>::New();
  imapper->SetInputConnection(imageDataGeometryFilter->GetOutputPort());
  imapper->ScalarVisibilityOff();
  vtkSmartPointer<vtkActor> iactor = vtkSmartPointer<vtkActor>::New();
  iactor->SetMapper(imapper);
  iactor->GetProperty()->SetPointSize(1);
  iactor->GetProperty()->SetColor(0.0, 0.0, 1.0);

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
  renderer->AddActor(iactor);
  renderer->SetBackground(0.8, .8, .8); 

  renderWindow->Render();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
