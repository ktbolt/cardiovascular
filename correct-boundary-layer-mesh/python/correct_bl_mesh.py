
import sys
import os
import vtk

def compute_model_normals(surface):
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(surface)
    normals.SplittingOn()
    normals.SetFeatureAngle(60.0)
    normals.ComputeCellNormalsOn()
    normals.ComputePointNormalsOn()
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.Update()

    new_surface = normals.GetOutput()
    new_surface.BuildLinks()
    return new_surface

def get_surface_faces(surface):
    '''Get the faces from the surface mesh using the ModelFaceID data array.
    '''
    face_ids = surface.GetCellData().GetArray('ModelFaceID')
    face_ids_range = 2*[0]
    face_ids.GetRange(face_ids_range, 0)
    min_id = int(face_ids_range[0])
    max_id = int(face_ids_range[1])

    ## Extract face geometry.
    #
    faces = []
    for i in range(min_id, max_id+1):
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(surface)
        threshold.SetInputArrayToProcess(0,0,0,1,'ModelFaceID')
        threshold.ThresholdBetween(i,i)
        threshold.Update();

        surfacer = vtk.vtkDataSetSurfaceFilter()
        surfacer.SetInputData(threshold.GetOutput())
        surfacer.Update()
        faces.append(surfacer.GetOutput())

    return faces

def add_line(renderer, pt1, pt2, color=[1.0, 1.0, 1.0], width=2):
    line = vtk.vtkLineSource()
    line.SetPoint1(pt1);
    line.SetPoint2(pt2)
    line.Update()
    polydata = line.GetOutput()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(width)
    renderer.AddActor(actor)

def show_point_normals(renderer, surface):
    points = surface.GetPoints()
    normals = surface.GetPointData().GetArray('Normals')
    scale = 0.2

    for i in range(0, surface.GetNumberOfPoints()):
        point1 = surface.GetPoint(i)
        normal = [ -normals.GetComponent(i,j) for j in range(3)]
        point2 = [ point1[j] + scale*normal[j] for j in range(3)]
        add_line(renderer, point1, point2, color=[0.0, 0.5, 0.0], width=4)

def create_graphics_geometry(geom):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    mapper.SetScalarVisibility(False)
    actor = vtk.vtkActor()
    actor.GetProperty().SetColor(1.0, 0.0, 0.0)
    #actor.GetProperty().SetOpacity(0.5)
    #actor.GetProperty().BackfaceCullingOn()
    actor.SetMapper(mapper)
    return actor

def read_vtu(file_name):
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()

    surfacer = vtk.vtkDataSetSurfaceFilter()
    surfacer.SetInputData(mesh)
    surfacer.Update()
    surface = surfacer.GetOutput()

    return mesh, surface

def read_model(file_name):
    '''Read in a model surface mesh.
    '''
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    return reader.GetOutput()

if __name__ == '__main__':

    # Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.7, 0.7, 0.7)
    renderer_win.SetSize(1000, 1000)

    # Read the model.
    file_name = 'tappered-cyl.vtp'
    model_surface = read_model(file_name)
    model_geom = create_graphics_geometry(model_surface)
    #model_geom.GetProperty().SetOpacity(0.5)
    model_geom.GetProperty().EdgeVisibilityOn()
    model_geom.GetProperty().SetEdgeColor(0,0,0)
    renderer.AddActor(model_geom)
    new_model_surface = compute_model_normals(model_surface)
    show_point_normals(renderer, new_model_surface)

    # Get the model faces.
    model_faces = get_surface_faces(model_surface)
    cap_geom = create_graphics_geometry(model_faces[1])
    cap_geom.GetProperty().SetColor(1,0,0)
    #face_geom.GetProperty().EdgeVisibilityOn()
    #renderer.AddActor(cap_geom)
    #
    wall_geom = create_graphics_geometry(model_faces[0])
    wall_geom.GetProperty().SetColor(0,0,1)
    #face_geom.GetProperty().EdgeVisibilityOn()
    #renderer.AddActor(wall_geom)

    # Read surface used for boundary layer mesh vtu.
    file_name = 'boundarylayermesh_normals.vtu'
    mesh, surface_normals = read_vtu(file_name)
    # Show point normals.
    # show_point_normals(renderer, surface_normals)

    # Read boundary layer mesh vtu.
    file_name = 'boundarylayermesh.vtu'
    mesh, surface = read_vtu(file_name)

    # Show surface.
    surface_geom = create_graphics_geometry(surface)
    surface_geom.GetProperty().EdgeVisibilityOn()
    #surface_geom.GetProperty().SetRepresentationToWireframe()
    #renderer.AddActor(surface_geom)

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    interactor.Start()




