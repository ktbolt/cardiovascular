'''Convert a CFD General Notation System (cgns) file into a VTK VTU format file.

   The cgns file is assumed to have been created by Ansys.

   Usage:

      python convert-cgns.py FILE_NAME [paths]

      If 'paths' is given then only the cgns data hierarchy is printed.
'''
import h5py
import numpy as np
import os 
import sys
import vtk 

def traverse_datasets(hdf_file):
    '''Traverse the cgns data hierarchy.
    '''
    def h5py_dataset_iterator(g, prefix=''):
        for key in g.keys():
            item = g[key]
            path = f'{prefix}/{key}'
            if isinstance(item, h5py.Dataset): # test for dataset
                yield (path, item)
            elif isinstance(item, h5py.Group): # test for group (go down)
                yield from h5py_dataset_iterator(item, path)

    for path, _ in h5py_dataset_iterator(hdf_file):
        yield path

def print_paths(mesh_file):
    '''Print all the paths in the cgns data hierarchy.
    '''
    print('---------- cgns data hierarchy ---------- ')
    for dset in traverse_datasets(mesh_file):
        print(dset)

def get_path(mesh_file, query):
    for dset in traverse_datasets(mesh_file):
        if query in dset:
            return dset
    return None

def get_mesh_coordinates(mesh_file):
    '''Get the mesh from the cgns file coordinates.
    '''
    print("\nGet mesh coordinates ")
    x_coords_path = get_path(mesh_file, 'GridCoordinates/CoordinateX')
    print("X coords path: " + x_coords_path)
    x = mesh_file[x_coords_path]

    y_coords_path = get_path(mesh_file, 'GridCoordinates/CoordinateY')
    print("Y coords path: " + y_coords_path)
    y = mesh_file[y_coords_path]

    z_coords_path = get_path(mesh_file, 'GridCoordinates/CoordinateZ')
    print("Z coords path: " + z_coords_path)
    z = mesh_file[z_coords_path]

    coordinates = np.column_stack([x, y, z])
    print("Shape of coordinates: " + str(coordinates.shape))

    return coordinates 

def get_mesh_element_connectivity(mesh_file, tetrahedra=True):
    '''Get the mesh element connectivity from the cgns file .
    '''
    print("\nGet mesh element connectivity")
    if tetrahedra:
        elem_type = 'Elem_Tetras'
    else:
        elem_type = 'Elem_Wedges'
    print("Element type: " + elem_type)

    conn_size_path = get_path(mesh_file, elem_type+'/ElementRange')
    print("Conn size path: " + conn_size_path)
    idx_min, idx_max = mesh_file[conn_size_path]
    print("idx_min: {0:d}".format(idx_min))
    print("idx_max: {0:d}".format(idx_max))

    num_elems = idx_max - idx_min + 1
    idx_min = 1
    idx_max = num_elems
    print("Number of elements: {0:d}".format(num_elems))

    conn_path = get_path(mesh_file, elem_type+'/ElementConnectivity')
    print("Conn path: " + conn_path)
    conn_data = mesh_file[conn_path]
    connectivity = np.array(conn_data).reshape(idx_max, -1) - 1

    return connectivity 

def create_unstructured_grid(coordinates, elem_conn, elem_type):
    '''Create a vtkUnstructuredGrid for the given element type.
    '''
    ugrid = vtk.vtkUnstructuredGrid()

    points = vtk.vtkPoints()
    for pt in coordinates:
        points.InsertNextPoint(pt[0], pt[1], pt[2])
    ugrid.SetPoints(points)

    if elem_type == vtk.VTK_TETRA:
        ElemClass = vtk.vtkTetra
        num_elem_nodes = 4
    elif elem_type == vtk.VTK_WEDGE:
        ElemClass = vtk.vtkWedge
        num_elem_nodes = 6

    cell_array = vtk.vtkCellArray()
    for cell in elem_conn:
        elem = ElemClass()
        for i in range(num_elem_nodes):
            elem.GetPointIds().SetId(i, cell[i])
        cell_array.InsertNextCell(elem)

    ugrid.SetCells(elem_type, cell_array)

    return ugrid

def write_vtu(file_base_name, coordinates, tets_conn, wedges_conn):
    '''Write the mesh as a .vtu file.

       The vtk.vtkUnstructuredGrid.SetCells() method did not work for multiple cell types
       so create a separate vtkUnstructuredGrid for each cell type and append them.
    '''
    append_filter = vtk.vtkAppendFilter()

    if len(tets_conn) != 0:
        tets_ugrid = create_unstructured_grid(coordinates, tets_conn, vtk.VTK_TETRA)
        append_filter.AddInputData(tets_ugrid)

    if len(wedges_conn) != 0:
        wedges_ugrid = create_unstructured_grid(coordinates, wedges_conn, vtk.VTK_WEDGE)
        append_filter.AddInputData(wedges_ugrid)
    
    append_filter.Update()
    ugrid = append_filter.GetOutput()
    
    # Write the VTU file.
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputData(ugrid)
    writer.SetFileName(file_base_name + '.vtu')
    writer.Update()

if __name__ == '__main__':

    file_name = sys.argv[1]
    file_base_name, ext = os.path.splitext(file_name)
    mesh_file = h5py.File(file_name, "r")

    if (len(sys.argv) == 3) and (sys.argv[2] == 'paths'):
        print_paths(mesh_file)
        sys.exit(0)

    # Get the mesh coordinates.
    coordinates = get_mesh_coordinates(mesh_file)

    # Get the mesh element connectivity.
    tets_conn = get_mesh_element_connectivity(mesh_file, tetrahedra=True)
    wedges_conn = get_mesh_element_connectivity(mesh_file, tetrahedra=False)

    # Write the mesh as a .vtu file.
    write_vtu(file_base_name, coordinates, tets_conn, wedges_conn)

