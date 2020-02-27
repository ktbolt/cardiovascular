
// The Image class is used to 

#include <iostream>
#include <string>
#include <vector>
#include <iostream>

#include "Graphics.h"

#include <vtkActor.h>

#ifndef IMAGE_H 
#define IMAGE_H 

class Image {

  public:
    Image();

    vtkSmartPointer<vtkActor> sliceActor;

  private:
    vtkSmartPointer<vtkPolyData> m_Polydata;
};

#endif

