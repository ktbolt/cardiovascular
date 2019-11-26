"""
This script is used to print mesh information for a mesh created by the SimVascular 'SV Meshing' tool.

    1) Nodal coordinates

    2) Node element lists

    3) Surface nodal coordinates

    4) Surface node element lists

A Mesh name corresponds to a data node under the SimVascular 'SV Data Manager' 'Meshes' node. 

Example: SimVascular DemoProject

    >>> demo_mesh = MeshInfo('demo')
    >>> demo_mesh.print_nodes()

Mesh information can also be printed to a file. A file is opened and the file object 
passed as an optional argument.

Example: SimVascular DemoProject

    >>> demo_mesh = MeshInfo('demo')
    >>> node_file = 'node-coords.txt'
    >>> with open(node_file, 'w') as file:
    >>>     mesh_info.print_nodes(file)
"""
import sv
import sys
import vtk

class MeshInfo(object):
    """ 
    This class is used to print mesh information. 
    """
    def __init__(self, mesh_name):
        """ Initialize the MeshInfo object
        Args:
            mesh_name (string): The name of a SimVascular Meshes data node.
        """
        self.mesh_name = mesh_name
        self.repo_mesh_name = mesh_name + 'Repo'
        print('[MeshInfo] Repository name: {0:s}'.format(self.repo_mesh_name))

        # Add the Mesh to the Repository.
        if int(sv.Repository.Exists(self.repo_mesh_name)):
            print('[MeshInfo] {0:s} is already in the repository.'.format(self.repo_mesh_name))
        else:
            sv.GUI.ExportMeshToRepos(self.mesh_name, self.repo_mesh_name)
            print('[MeshInfo] Add {0:s} to the repository.'.format(self.repo_mesh_name))

        # Get the vtk unstructure mesh.
        self.unstructured_grid = sv.Repository.ExportToVtk(self.repo_mesh_name)
        self.unstructured_grid.BuildLinks()
        self.num_nodes = self.unstructured_grid.GetNumberOfPoints()
        self.nodes = self.unstructured_grid.GetPoints()
        self.num_elements = self.unstructured_grid.GetNumberOfCells()

        # Get the surface mesh.
        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputData(self.unstructured_grid)
        surface_filter.Update()
        self.surface = surface_filter.GetOutput()

        # Print some basic mesh information. 
        print('[MeshInfo] Number of nodes: {0:3d}'.format(self.num_nodes))
        print('[MeshInfo] Number of elements: {0:3d}'.format(self.num_elements))
        num_nodes = self.surface.GetNumberOfPoints()
        num_elements = self.surface.GetNumberOfCells()
        print('[MeshInfo] ') 
        print('[MeshInfo] Number of surface nodes: {0:3d}'.format(num_nodes))
        print('[MeshInfo] Number of surface elements: {0:3d}'.format(num_elements))

    def print_nodes(self, ofile = sys.stdout):
        """ 
        Print the mesh nodal coordinates. 
        """
        print('[MeshInfo.print_nodes] ---------- Mesh nodal coordinates ---------- ', file=ofile)
        node_ids = self.unstructured_grid.GetCellData().GetArray('GlobalNodeID')
        if node_ids == None:
            print('[MeshInfo.print_nodes] WARNING: No node IDs.')
        point = 3*[0.0]
        for i in range(0, self.num_nodes):
            self.nodes.GetPoint(i, point)
            if node_ids != None:
                node_id = node_ids.GetValue(i)
                print("Node {0:d}: {1:d}  {2:f}  {3:f}  {4:f} ".format(i, node_id, point[0], point[1], point[2]), file=ofile)
            else:
                print("Node {0:d}: {1:f}  {2:f}  {3:f} ".format(i, point[0], point[1], point[2]), file=ofile)
        #_for i in range(0, self.num_nodes)
    #_print_nodes(self)

    def print_node_elements(self, ofile = sys.stdout):
        """ 
        Print the mesh nodal elements. 
        """
        print('[MeshInfo.print_nodes] ---------- Mesh nodal elements ---------- ', file=ofile)
        for i in range(0, self.num_nodes):
            cell_list = vtk.vtkIdList()
            self.unstructured_grid.GetPointCells(i, cell_list)
            cellIDs = ','.join([str(cell_list.GetId(j)) for j in range(cell_list.GetNumberOfIds())])
            print("Node {0:d}: elements: {1:s} ".format(i, cellIDs), file=ofile) 
    #_print_node_elements(self):

    def print_surface_nodes(self, ofile = sys.stdout):
        """ 
        Print the mesh surface_nodal coordinates. 
        """
        print('[MeshInfo.print_nodes] ---------- Mesh surface_nodal coordinates ---------- ', file=ofile)
        point = 3*[0.0]
        num_nodes = self.surface.GetNumberOfPoints()
        nodes = self.surface.GetPoints()
        for i in range(0, num_nodes):
            nodes.GetPoint(i, point)
            print("Node {0:d}: {1:f}  {2:f}  {3:f} ".format(i, point[0], point[1], point[2]), file=ofile)
        #_for i in range(0, self.num_nodes)
    #_print_nodes(self)

    def print_surface_node_elements(self, ofile = sys.stdout):
        """ 
        Print the mesh surface nodal elements. 
        """
        print('[MeshInfo.print_nodes] ---------- Mesh suface nodal elements ---------- ')
        num_nodes = self.surface.GetNumberOfPoints()
        num_elements = self.surface.GetNumberOfCells()
        print('[MeshInfo] Number of surface nodes: {0:3d}'.format(num_nodes), file=ofile)
        print('[MeshInfo] Number of surface elements: {0:3d}'.format(num_elements), file=ofile)
        for i in range(0, num_nodes):
            cell_list = vtk.vtkIdList()
            self.surface.GetPointCells(i, cell_list)
            cellIDs = ','.join([str(cell_list.GetId(j)) for j in range(cell_list.GetNumberOfIds())])
            print("Node {0:d}: elements: {1:s} ".format(i, cellIDs), file=ofile) 
        #_for i in range(0, num_nodes)
    #_print_surface_node_elements(self)
   
#_class MeshInfo(object)

## Test for DemoProject.
#
demo_test = True
mesh_name = "demo"

if demo_test:
    mesh_info = MeshInfo(mesh_name)
    #mesh_info.print_nodes()
    #mesh_info.print_node_elements()
    #mesh_info.print_surface_nodes()
    #mesh_info.print_surface_node_elements()
    #
    # Write nodal coordinates to a file.
    node_file = 'node-coords.txt'
    with open(node_file, 'w') as file:
        mesh_info.print_nodes(file)

