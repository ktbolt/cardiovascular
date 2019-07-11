
#include <vtkActor.h>
//
#include <vtkCellLocator.h>
//
#include <vtkDataSetMapper.h>
//
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkInteractorStyleUser.h>
//
#include <vtkLineSource.h>
//
#include <vtkNamedColors.h>
//
#include <vtkPlaneSource.h>
#include <vtkPointData.h>
#include <vtkPolyData.h>
#include <vtkPolyDataMapper.h>
#include <vtkPolyLine.h>
#include <vtkProperty.h>
#include <vtkPropPicker.h>
//
#include <vtkRegularPolygonSource.h>
#include <vtkRenderer.h>
#include <vtkRendererCollection.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
//
#include <vtkSelection.h>
#include <vtkSphereSource.h>
//
#include <vtkXMLPolyDataWriter.h>

#ifndef GRAPHICS_H
#define GRAPHICS_H

#include "Mesh.h"
#include "Centerlines.h"

class MouseMeshInteractorStyle;
class MouseCenterlineInteractorStyle;

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
    void SetCenterlines(Centerlines& centerlines);
    Mesh* GetMesh(); 
    void Start(); 
    void SetDataName(std::string name); 
    std::string GetDataName(); 
    vtkSmartPointer<vtkActor> CreateCircle();

  private:
    vtkSmartPointer<vtkDataSetMapper> p_Mapper;
    vtkSmartPointer<vtkRenderer> m_Renderer;
    vtkSmartPointer<vtkRenderWindow> m_RenderWindow;

    vtkSmartPointer<vtkRenderWindowInteractor> m_RenderWindowInteractor;
    vtkSmartPointer<MouseCenterlineInteractorStyle> m_InteractionStyle;
    //vtkSmartPointer<MouseMeshInteractorStyle> m_InteractionStyle;

    Mesh* m_Mesh;
    std::string m_DataName;
    Centerlines m_Centerlines;
};

//--------------------------
// MouseMeshInteractorStyle
//--------------------------
// Handle mouse events for a trackball interactor selecting a surface mesh.
//
class MouseMeshInteractorStyle : public vtkInteractorStyleTrackballCamera
{
  public:
    static MouseMeshInteractorStyle* New();
    vtkTypeMacro(MouseMeshInteractorStyle, vtkInteractorStyleTrackballCamera);
    MouseMeshInteractorStyle();
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


//----------------
// CenterLineEdit 
//----------------

class CenterLineEdit 
{
  public:
    CenterLineEdit() {}

    CenterLineEdit(vtkSmartPointer<vtkPolyData> surface, vtkSmartPointer<vtkPolyData> lines, std::string clFileName); 

    void create_cell_locator();
    void locate_cell(double point[3], int& index, double& radius, double normal[3], double tangent[3]);
    void write_centerline();

  private:

    std::string clFileName;
    int materialID;
    vtkIdType numCenterLineVerts;
    std::vector<int> centerLineMaterialIDs;
    vtkSmartPointer<vtkPolyData> surface; 
    vtkSmartPointer<vtkPolyData> centerlines;
    vtkSmartPointer<vtkCellLocator> cellLocator;
    vtkSmartPointer<vtkDoubleArray> radiusData;
    vtkSmartPointer<vtkDoubleArray> normalData;
    vtkSmartPointer<vtkDoubleArray> abscissaData;
    vtkSmartPointer<vtkPointSet> pointSet;
};

//--------------------------------
// MouseCenterlineInteractorStyle
//--------------------------------
// Handle mouse events for a centerline trackball interactor.
//
class MouseCenterlineInteractorStyle : public vtkInteractorStyleTrackballCamera
{
  public:
    MouseCenterlineInteractorStyle();
    static MouseCenterlineInteractorStyle* New();
    vtkTypeMacro(MouseCenterlineInteractorStyle, vtkInteractorStyleTrackballCamera);

    void SetCenterlines(Centerlines& centerlines);
    void SetGraphics(Graphics* graphics);
    void SelectCenterline();

    // Need to declare this to prevent Vtk from interpreting pre-defined
    // shortcut keys (e.g. 'e' to exit).
    virtual void OnChar() override { }

    virtual void OnKeyPress() override;
    //virtual void OnLeftButtonDown() override;

  private:
    double startPoint[3], endPoint[3];
    bool startSelected;
    vtkSmartPointer<vtkSphereSource> startSphere = nullptr; 
    vtkSmartPointer<vtkSphereSource> endSphere = nullptr; 
    vtkSmartPointer<vtkPlaneSource> startPlane = nullptr; 
    vtkSmartPointer<vtkPlaneSource> endPlane = nullptr; 
    Centerlines m_Centerlines;
    vtkSmartPointer<vtkLineSource> line; 
    Graphics* m_Graphics;

};

#endif 



