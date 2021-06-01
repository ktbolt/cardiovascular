#!/usr/bin/env python
'''This script is used to extract slices of results along a centerline geomatry. 
'''
from graphics import Graphics
import os
from os import path
import sys
import time
import vtk

def extract_all_slices(renderer, centerlines, mesh):
    print('[extract_all_slices] ')
    cl_points = centerlines.GetPoints()
    num_cl_points = centerlines.GetNumberOfPoints()
    normal_data = centerlines.GetPointData().GetArray("CenterlineSectionNormal")
    print('[extract_all_slices] Number of centerline points: {0:d}'.format(num_cl_points))

    plane_dist = mesh.GetPointData().GetArray("plane_dist")
    mesh.GetPointData().SetActiveScalars("plane_dist")
    num_mesh_pts = mesh.GetNumberOfPoints()
    mesh_points = mesh.GetPoints()

    cl_pt = 3*[0.0]
    mesh_pt = 3*[0.0]
    s = 2.0

    start_time = time.time()

    for i in range(200,400):
    #for i in range(2,num_cl_points-2):
        cl_points.GetPoint(i, cl_pt)
        normal = [normal_data.GetComponent(i,j) for j in range(3)]
        #pt = [ cl_pt[i] + s*normal[i] for i in range(3) ]
        #gr.add_line(renderer, cl_pt, pt, color=[1.0, 1.0, 1.0], width=2)

        for j in range(num_mesh_pts):
            mesh_points.GetPoint(j, mesh_pt)
            d = sum( [ normal[k] * (mesh_pt[k] - cl_pt[k]) for k in range(3) ] )
            plane_dist.SetValue(j, d)

        contour = vtk.vtkContourGrid()
        contour.SetInputData(mesh)
        contour.SetValue(0, 0.0)
        contour.Update()
        iso_surface = contour.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(iso_surface)
        conn_filter.SetExtractionModeToSpecifiedRegions()

        min_d = 1e6
        min_comp = None
        center = 3*[0.0]
        rid = 0
        cpt = 3*[0.0]
        
        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break

            conn_filter.DeleteSpecifiedRegion(rid)
            
            clean_filter = vtk.vtkCleanPolyData()
            clean_filter.SetInputData(component)
            clean_filter.Update();
            component = clean_filter.GetOutput()

            comp_points = component.GetPoints()
            num_comp_points = component.GetNumberOfPoints()
            num_comp_cells = component.GetNumberOfCells()

            cx = 0.0
            cy = 0.0
            cz = 0.0
            for j in range(num_comp_points):
                comp_points.GetPoint(j, cpt)
                cx += cpt[0]
                cy += cpt[1]
                cz += cpt[2]
            center[0] = cx / num_comp_points
            center[1] = cy / num_comp_points
            center[2] = cz / num_comp_points

            if d < min_d:
                min_d = d
                min_comp = component

            rid += 1
        #_while True

        if i % 10 == 0:
            gr.add_geometry(renderer, min_comp, color=[1.0,0,1])

    #_for i in range(num_cl_points)


    end_time = time.time()
    elapse_time = end_time - start_time
    time_per_cl_pt = elapse_time / num_cl_points
    print('[extract_all_slices] Elapse time: {0:g}'.format(elapse_time))
    print('[extract_all_slices] time per cl point: {0:g}'.format(time_per_cl_pt))


def extract_slice(**kwargs):
    '''Extract a slice at a picked point.
    '''
    #print('[extract_slice] ')
    node_id = kwargs['node_id']
    #print('[extract_slice] node_id: {0:s}'.format(str(node_id)))
    node_id = 75 

    centerlines = kwargs['pick_geometry']
    points = centerlines.GetPoints()
    node_pt = points.GetPoint(node_id)
    print('[extract_slice] point: {0:s}'.format(str(node_pt)))
    normal_data = centerlines.GetPointData().GetArray("CenterlineSectionNormal")
    normal = [normal_data.GetComponent(node_id,i) for i in range(3)]
    print('[extract_slice] normal: {0:s}'.format(str(normal)))

    graphics = kwargs['graphics']
    s = 2.0
    pt2 = [ node_pt[i] + s*normal[i] for i in range(3) ]
    graphics.add_line(node_pt, pt2, color=[1.0, 0.0, 0.0], width=2)

    mesh = kwargs['data']
    mesh_points = mesh.GetPoints()
    num_pts = mesh.GetNumberOfPoints()
    #print('[extract_slice] mesh num pts: {0:d}'.format(num_pts))
    plane_dist = mesh.GetPointData().GetArray("plane_dist")

    for i in range(num_pts):
        pt = mesh_points.GetPoint(i)
        d = sum( [ normal[j] * (pt[j] - node_pt[j])  for j in range(3) ] )
        plane_dist.SetValue(i, d)

    iso_surf = extract_isosurface(mesh, "plane_dist", 0.0)
    graphics.add_geometry(iso_surf, color=[0.5, 0.5, 0.5], wire=True)

    radius_data = centerlines.GetPointData().GetArray("MaximumInscribedSphereRadius")
    radius = radius_data.GetValue(node_id)
    #print('[extract_slice] radius: {0:g}'.format(radius))

    conn_filter = vtk.vtkPolyDataConnectivityFilter()
    conn_filter.SetInputData(iso_surf)
    conn_filter.SetExtractionModeToSpecifiedRegions()

    components = []
    boundary_faces = {}
    min_d = 1e6
    min_comp = None

    rid = 0
    center = 3*[0.0]
    while True:
        conn_filter.AddSpecifiedRegion(rid)
        conn_filter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(conn_filter.GetOutput())
        if component.GetNumberOfCells() <= 0:
            break

        #print('\n[extract_slice] ---- rid {0:d} ----'.format(rid))
        conn_filter.DeleteSpecifiedRegion(rid)

        if rid == 0:
            color = [1.0, 0.0, 0.0]
        elif rid == 1:
            color = [0.0, 1.0, 0.0]
        else:
            color = [0.0, 0.0, 1.0]

        clean_filter = vtk.vtkCleanPolyData()
        clean_filter.SetInputData(component)
        clean_filter.Update();
        component = clean_filter.GetOutput()

        comp_points = component.GetPoints()
        num_comp_points = component.GetNumberOfPoints()
        num_comp_cells = component.GetNumberOfCells()

        cx = 0.0
        cy = 0.0
        cz = 0.0
        for i in range(num_comp_points):
            pt = comp_points.GetPoint(i)
            cx += pt[0]
            cy += pt[1]
            cz += pt[2]
        center[0] = cx / num_comp_points
        center[1] = cy / num_comp_points
        center[2] = cz / num_comp_points
        #components.append(component)
        d = sum( [ (center[j]-node_pt[j])*(center[j]-node_pt[j])  for j in range(3) ] )
        #print('[extract_slice] num_comp_cells: {0:d}'.format(num_comp_cells))
        #print('[extract_slice] num_comp_points: {0:d}'.format(num_comp_points))
        #print('[extract_slice] center: {0:s}'.format(str(center)))
        #print('[extract_slice] d: {0:g}'.format(d))
        if d < min_d:
            min_d = d
            min_comp = component
        rid += 1

    #print('[extract_slice] min_d: {0:g}'.format(min_d))
    graphics.add_geometry(min_comp, color=[1.0,0,1])

def extract_isosurface(mesh, name, iso_value):
    data = mesh.GetPointData().GetArray(name)
    #data_range = 2*[0]
    #data.GetRange(data_range, 0)
    #min_val = int(data_range[0])
    #max_val = int(data_range[1])
    #print("[extract_isosurface] range: {0:d} {1:d}".format(min_val, max_val))
    mesh.GetPointData().SetActiveScalars(name)

    '''
    mc = vtk.vtkMarchingCubes()
    mc.SetInputData(mesh)
    #mc.SetInputData(data)
    mc.SetValue(0, iso_value)
    mc.ComputeNormalsOn()
    mc.ComputeNormalsOn()
    iso_surface = mc.GetOutput()
    '''

    #contour = vtk.vtkContour3DLinearGrid() 
    contour = vtk.vtkContourGrid()
    contour.SetInputData(mesh)
    contour.SetValue(0, iso_value)
    contour.Update()
    iso_surface = contour.GetOutput()

    return iso_surface 

def read_mesh(file_name):
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

def read_centerlines(file_name):
    '''Read a centerlines geometry file created using SV.
    '''
    filename, file_extension = path.splitext(file_name)
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    geometry = reader.GetOutput()
    return geometry 

def main():

    ## Create graphics interface.   
    graphics = Graphics()

    file_name = 'centerlines.vtp'
    centerlines = read_centerlines(file_name)
    graphics.add_geometry(centerlines, color=[0.0, 0.6, 0.0], line_width=3)

    file_name = 'all_results_00500.vtu'
    mesh, surface = read_mesh(file_name)
    #graphics.add_geometry(surface, color=[0.8, 0.8, 0.8], wire=True)

    num_pts = mesh.GetNumberOfPoints()
    print('[main] mesh num pts: {0:d}'.format(num_pts))
    plane_dist = vtk.vtkDoubleArray()
    plane_dist.SetName("plane_dist")
    plane_dist.SetNumberOfComponents(1)
    plane_dist.SetNumberOfTuples(num_pts)
    for i in range(num_pts):
        plane_dist.SetValue(i,0.0)
    mesh.GetPointData().AddArray(plane_dist)

    # extract_all_slices(renderer, centerlines, mesh)

    ## Create a mouse interactor for selecting centerline points.
    picking_keys = ['c']
    event_table = None
    event_table = {
        'c': (extract_slice, mesh),
    }

    graphics.init_picking(centerlines, picking_keys, event_table)

    ## Display window.
    graphics.show()

if __name__ == '__main__':
    main()
