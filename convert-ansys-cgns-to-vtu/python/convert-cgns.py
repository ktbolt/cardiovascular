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

def get_mesh_element_connectivity(mesh_file):
    '''Get the mesh element connectivity from the cgns file .
    '''
    print("\nGet mesh element connectivity")
    conn_size_path = get_path(mesh_file, 'ElementRange')
    print("Conn size path: " + conn_size_path)
    idx_min, idx_max = mesh_file[conn_size_path]
    print("idx_min: {0:d}".format(idx_min))
    print("idx_max: {0:d}".format(idx_max))

    conn_path = get_path(mesh_file, 'ElementConnectivity')
    print("Conn path: " + conn_path)
    conn_data = mesh_file[conn_path]
    connectivity = np.array(conn_data).reshape(idx_max, -1) - 1

    return connectivity 

def write_vtu(file_base_name, coordinates, connectivity):
    '''Write the mesh as a .vtu file.
    '''

    ## Create the vtkUnstructuredGrid data.
    #
    ugrid = vtk.vtkUnstructuredGrid()

    points = vtk.vtkPoints()
    for pt in coordinates:
        points.InsertNextPoint(pt[0], pt[1], pt[2])
    
    ugrid.SetPoints(points)
    cell_array = vtk.vtkCellArray()

    for cell in connectivity:
        tet = vtk.vtkTetra()
        for i in range(4):
            tet.GetPointIds().SetId(i, cell[i])
        cell_array.InsertNextCell(tet)

    ugrid.SetCells(vtk.VTK_TETRA, cell_array)

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
    connectivity = get_mesh_element_connectivity(mesh_file)

    # Write the mesh as a .vtu file.
    write_vtu(file_base_name, coordinates, connectivity)
