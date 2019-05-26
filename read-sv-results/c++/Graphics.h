
#include <vtkActor.h>
//
#include <vtkDataSetMapper.h>
//
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkInteractorStyleUser.h>
//
#include <vtkNamedColors.h>
//
#include <vtkPolyData.h>
#include <vtkProperty.h>
//
#include <vtkRenderer.h>
#include <vtkRendererCollection.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
//
#include <vtkSelection.h>

#ifndef GRAPHICS_H
#define GRAPHICS_H

#include "Mesh.h"

//class Mesh;
class MouseInteractorStyle;

//----------
// Graphics
//----------
//
class Graphics {

  public:
    Graphics(); 
    void AddGeometry(vtkSmartPointer<vtkActor> geom);
    vtkSmartPointer<vtkActor> CreateGeometry(vtkSmartPointer<vtkPolyData> poly_data);
    void SetMesh(Mesh* mesh); 
    Mesh* GetMesh(); 
    void Start(); 
    void SetDataName(std::string name); 
    std::string GetDataName(); 

  private:
    vtkSmartPointer<vtkDataSetMapper> p_Mapper;
    vtkSmartPointer<vtkRenderer> m_Renderer;
    vtkSmartPointer<vtkRenderWindow> m_RenderWindow;

    vtkSmartPointer<vtkRenderWindowInteractor> m_RenderWindowInteractor;
    vtkSmartPointer<MouseInteractorStyle> m_InteractionStyle;

    Mesh* m_Mesh;
    std::string m_DataName;

};

//----------------------
// MouseInteractorStyle
//----------------------
// Handle mouse events for a trackball interactor.
//
class MouseInteractorStyle : public vtkInteractorStyleTrackballCamera
{
  public:
    static MouseInteractorStyle* New();
    vtkTypeMacro(MouseInteractorStyle, vtkInteractorStyleTrackballCamera);
    MouseInteractorStyle();
    void SetGraphics(Graphics* graphics);
    void SelectMesh(int cellID);

    // Need to declare this to prevent Vtk from interpreting pre-defined
    // shortcut keys (e.g. 'e' to exit).
    virtual void OnChar() override { }

    virtual void OnKeyPress() override;
    //virtual void OnLeftButtonDown() override;

  private:
    vtkSmartPointer<vtkDataSetMapper> m_SelectedMapper;
    vtkSmartPointer<vtkActor> m_SelectedActor;
    Graphics* m_Graphics;
    vtkSmartPointer<vtkNamedColors> m_Colors;

    void SelectCell();
    void AddSelection(int cellID);
    void SelectSurfaceMesh(int cellID, vtkSmartPointer<vtkSelection> selection);
 
};

//vtkStandardNewMacro(MouseInteractorStyle);

#endif 



