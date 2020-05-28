''' This script is used to read in a bct.vtp file.  

    It prints out the node IDs and coordinates for each entry in the file.
'''
from collections import defaultdict 
import os
import sys
import vtk
from math import sqrt

def add_mesh_geom(reader, mesh, renderer):
    ''' Add mesh to renderer.
    '''
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    mapper.ScalarVisibilityOff();

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToPoints()
    #actor.GetProperty().SetRepresentationToWireframe()
    #actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().BackfaceCullingOn()   
    #actor.GetProperty().SetDiffuseColor(0, 0.5, 0) 
    actor.GetProperty().SetEdgeVisibility(1) 
    actor.GetProperty().SetOpacity(0.5) 
    #actor.GetProperty().SetEdgeColor(1, 0, 0) 
    actor.GetProperty().SetColor(0.0, 0.8, 0.8)
    #actor.GetProperty().SetPointSize(5)
    renderer.AddActor(actor)


def print_data(mesh):
    num_points = mesh.GetNumberOfPoints()
    points = mesh.GetPoints()
    num_cells = mesh.GetNumberOfCells()

    print("Nodel coordinates: ") 
    node_ids = mesh.GetPointData().GetArray('GlobalNodeID')
    pt = 3*[0.0]
    for i in range(num_points):
        nid = node_ids.GetValue(i)
        points.GetPoint(i, pt)
        print("i:{0:d} nodeID:{1:d}  point:{2:s}".format(i, nid, str(pt)))

if __name__ == '__main__':

    ## Read vtp file.
    #
    file_name = sys.argv[1]
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()
    print_data(mesh)

    # Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    add_mesh_geom(reader, mesh, renderer)

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    interactor.Start()


