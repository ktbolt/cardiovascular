
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
    void add_geometry(vtkActor* geom);
    vtkActor* create_geometry(vtkPolyData* poly_data);
    void set_mesh(Mesh* mesh); 
    void set_centerlines(Centerlines* centerlines);
    Mesh* get_mesh(); 
    void start(); 
    void set_data_name(const std::string& name); 
    std::string get_data_name(); 
    vtkActor* create_circle();
    void refresh();

    vtkSmartPointer<vtkDataSetMapper> mapper_;
    vtkSmartPointer<vtkRenderer> renderer_;
    vtkSmartPointer<vtkRenderWindow> render_window_;

    vtkSmartPointer<vtkRenderWindowInteractor> render_window_interactor_;
    vtkSmartPointer<MouseCenterlineInteractorStyle> interaction_style_;
    //vtkSmartPointer<MouseMeshInteractorStyle> m_InteractionStyle;

    Mesh* mesh_;
    std::string data_name_;
    Centerlines* centerlines_;
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
    void set_graphics(Graphics* graphics);
    void select_mesh(int cellID);

    // Need to declare this to prevent Vtk from interpreting pre-defined
    // shortcut keys (e.g. 'e' to exit).
    virtual void OnChar() override { }

    virtual void OnKeyPress() override;
    //virtual void OnLeftButtonDown() override;

    void select_cell();
    void add_selection(int cellID);
    //void selectSurfaceMesh(int cellID, vtkSmartPointer<vtkSelection> selection);

    vtkDataSetMapper* selected_mapper_;
    vtkActor* selected_actor_;
    Graphics* graphics_;
    vtkNamedColors* colors_;
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

    void set_centerlines(Centerlines* centerlines);
    void set_graphics(Graphics* graphics);
    void select_centerline();
    void slice_mesh();

    // Need to declare this to prevent Vtk from interpreting pre-defined
    // shortcut keys (e.g. 'e' to exit).
    virtual void OnChar() override { }

    virtual void OnKeyPress() override;
    //virtual void OnLeftButtonDown() override;

    double startPoint[3], endPoint[3];
    bool startSelected;
    vtkSmartPointer<vtkSphereSource> startSphere = nullptr; 
    vtkSmartPointer<vtkSphereSource> endSphere = nullptr; 
    vtkSmartPointer<vtkPlaneSource> startPlane = nullptr; 
    vtkSmartPointer<vtkPlaneSource> endPlane = nullptr; 
    Centerlines* centerlines_;
    vtkSmartPointer<vtkLineSource> line; 
    Graphics* graphics_;

};

#endif 



