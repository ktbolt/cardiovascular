#!/usr/bin/env python

from collections import defaultdict
from collections import OrderedDict
from math import sqrt
from math import cos
from math import acos
from math import pi
from math import degrees
from os import path
import sv
import vtk

class Surface(object):
    '''The surface class is used to store surface data.
    '''
    def __init__(self, graphics=None, window=None, renderer=None):
        self.file_name = None
        self.file_prefix = None
        self.graphics = graphics
        self.window = window 
        self.renderer = renderer
        self.geometry = None
        self.sample_distance = 1.0
        self.average_normals = True
        self.slices = []
        self.length_scale = None
        self.vtk_actor = None

    def read(self, file_name):
        '''Read in a surface from a .vtp or .stl file.
        '''
        file_prefix, file_extension = path.splitext(file_name)
        self.file_name = file_name
        self.file_prefix = file_prefix 
        if file_extension not in ['.stl', '.vtp']:
            raise Exception("Unsupported file format '{0:s}'".format(file_extension))

        ## Create a solid model from the surface.
        #
        # This cleans up the surface and computes cell normals.
        #
        kernel = sv.modeling.Kernel.POLYDATA
        modeler = sv.modeling.Modeler(kernel)
        model = modeler.read(file_name)
        try:
            face_ids = model.get_face_ids()
        except:
            face_ids = model.compute_boundary_faces(angle=60.0)
        geometry = model.get_polydata()

        pd_normals = vtk.vtkPolyDataNormals()
        pd_normals.SetInputData(geometry)
        pd_normals.SplittingOff()
        pd_normals.ComputeCellNormalsOn()
        pd_normals.ComputePointNormalsOn()
        pd_normals.ConsistencyOn()
        pd_normals.AutoOrientNormalsOn()
        pd_normals.Update()
        self.geometry = pd_normals.GetOutput() 
        self.geometry.BuildLinks()

    def add_centerlines_source_node(self, **kwargs):
        '''Add a source node ID used for exctracting centerlines.
        '''
        if 'undo' in kwargs:
            print('[surface] undo source node')
            try:
                self.centerlines_source_nodes.pop()
                self.centerlines_source_cells.pop()
            except:
                pass 
            return

        node_id = kwargs['node_id']
        cell_id = kwargs['cell_id']
        self.centerlines_source_nodes.append(node_id)
        self.centerlines_source_cells.append(cell_id)

    def add_centerlines_target_node(self, **kwargs):
        '''Add a target node ID used for exctracting centerlines.
        '''
        if 'undo' in kwargs:
            try:
                self.centerlines_target_nodes.pop()
                self.centerlines_target_cells.pop()
            except:
                pass 
            return

        node_id = kwargs['node_id']
        node_id = kwargs['node_id']
        cell_id = kwargs['cell_id']
        self.centerlines_target_nodes.append(node_id)
        self.centerlines_target_cells.append(cell_id)

    def add_centerlines(self, centerlines_polydata):
        self.centerlines = centerlines_polydata
        if self.graphics != None and self.renderer != None:
            self.graphics.add_geometry(self.renderer, centerlines_polydata, color=[0.8, 0.0, 0.0], line_width=4)
            self.graphics.add_glyph_points(self.renderer, centerlines_polydata.GetPoints(), color=[0.0, 0.8, 0.0], size=10)
            self.vtk_actor.GetProperty().SetOpacity(0.4)
            self.vtk_actor.GetProperty().BackfaceCullingOn()
            self.window.Render()

    def extract_slices(self, **kwargs):
        '''Extract slices along centerline geometry.
     
           The centerline points are sampled using the sampling distance
           value which is used to select points that are separated by 
           this distace. 
 
           Centerline normals are averaged over the sampling distance to give
           provide a better representation of the slice orientation wrt to
           the surface.
        '''
        print("[surface] ========== extract_slices ==========")
        print(f"[surface] Sample distance: {self.sample_distance}")
        print(f"[surface] Average normals: {self.average_normals}")

        # Turn off INFO messages from vtk.vtkCutter.
        vtk.vtkLogger.SetStderrVerbosity(vtk.vtkLogger.VERBOSITY_OFF)

        points = self.centerlines.GetPoints()
        num_points = self.centerlines.GetNumberOfPoints()
        normal_data = self.centerlines.GetPointData().GetArray("CenterlineSectionNormal")
        max_radius_data = self.centerlines.GetPointData().GetArray('MaximumInscribedSphereRadius')
        print(f"[surface] Number of centerline points: {num_points}")

        start_id = 1
        end_id = num_points - 1
        id_offset = 1
        first_slice = True
        sample_dist = self.sample_distance

        plane_pt = 3*[0.0]
        last_plane_pt = 3*[0.0]
        avg_normal = 3*[0.0]

        for i in range(start_id, end_id, id_offset):
            plane_pt = points.GetPoint(i)
            plane_normal = [normal_data.GetComponent(i,j) for j in range(3)]
            compute_slice = False
            if self.average_normals:
                for j in range(3):
                    avg_normal[j] += plane_normal[j]
            else:
                for j in range(3):
                    avg_normal[j] = plane_normal[j]

            if not first_slice:
                dist = sqrt(sum([ (last_plane_pt[j]-plane_pt[j]) * (last_plane_pt[j]-plane_pt[j])  for j in range(3)]))
                if dist > sample_dist:
                    compute_slice = True
            else:
                compute_slice = True

            if compute_slice:
                length = vtk.vtkMath.Normalize(avg_normal)
                for j in range(3):
                    avg_normal[j] /= length 

                slice_plane = vtk.vtkPlane()
                slice_plane.SetOrigin(plane_pt[0], plane_pt[1], plane_pt[2])
                slice_plane.SetNormal(avg_normal[0], avg_normal[1], avg_normal[2])
                self.show_plane(plane_pt, avg_normal, color=[1,0,0])

                cutter = vtk.vtkCutter()
                cutter.SetCutFunction(slice_plane)
                cutter.SetInputData(self.geometry);
                cutter.Update()
                slice_geom = cutter.GetOutput()

                self.graphics.add_geometry(self.renderer, slice_geom, [1,0,0], line_width=3)
                self.slices.append(slice_geom)
                last_plane_pt = plane_pt

                for j in range(3):
                    avg_normal[j] = 0.0

            first_slice = False

        self.write_slices()

    def write_slices(self):
        '''Write slice geometry to a text file.
        '''
        slices_file = self.file_prefix + '-slices.txt'

        with open(slices_file, 'w') as file:
            for slice in self.slices:
                file.write("<contour_points>\n")
                num_points = slice.GetNumberOfPoints()
                points = slice.GetPoints()
                for i in range(num_points):
                    pt = points.GetPoint(i)
                    file.write(f'<point id="{i}" x="{pt[0]}"    y="{pt[1]}"  z="{pt[2]}" /> \n')
                file.write("</contour_points>\n")


    def show_plane(self, origin, normal, color):
        if not self.renderer:
            return
        plane = vtk.vtkPlaneSource()
        plane.SetCenter(origin)
        plane.SetNormal(normal)
        plane.Update()
        plane_pd = plane.GetOutput()
        self.graphics.add_geometry(self.renderer, plane_pd, color)

    def compute_centerlines(self, **kwargs):
        '''Compute the centerlines for the given list of node IDs.
        '''
        print('[surface] ========== compute_centerlines ==========')
        if len(self.centerlines_source_nodes) == 0:
            raise Exception("No source nodes have been selected for centerlines extraction.")

        if len(self.centerlines_target_nodes) == 0:
            raise Exception("No target nodes have been selected for centerlines extraction.")
       
        print('[surface] Source nodes: {0:s}'.format(str(self.centerlines_source_nodes)))
        print('[surface] Target nodes: {0:s}'.format(str(self.centerlines_target_nodes)))

        # Extract centerlines.
        surface = kwargs['surface']
        inlet_ids = self.centerlines_source_nodes 
        outlet_ids = self.centerlines_target_nodes 
        centerlines_polydata = sv.vmtk.centerlines(surface, inlet_ids, outlet_ids)
        #centerlines_polydata = sv.vmtk.centerlines(self.geometry, inlet_ids, outlet_ids)
        self.centerlines = centerlines_polydata
        if self.graphics != None and self.renderer != None:
            self.graphics.add_geometry(self.renderer, centerlines_polydata, color=[0.0, 0.8, 0.0], line_width=3)
            surface_obj = kwargs['data']
            surface_obj.vtk_actor.GetProperty().SetOpacity(0.7)
            surface_obj.vtk_actor.GetProperty().BackfaceCullingOn()
            self.window.Render()

        # Write centerlines.
        file_prefix = self.file_prefix
        file_name = file_prefix+"-centerlines.vtp"
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(centerlines_polydata)
        writer.Update()
        writer.Write()
        print("[surface] Centerlines geometry has been written to '{0:s}'".format(file_name))

    def get_connected_cells(self, cell_id, cell_normal, cell_adj, cell_edges, normals, cell_visited, level_num):
        '''Get the cells connected to the cell_id cell.
        '''
        #print('\n========== get_connected_cells adj_cell_id: {0:d} =========='.format(cell_id))
        tol = 0.99
        #print('[get_connected_cells] cell_normal: {0:s} '.format(str(cell_normal)))
        all_conn_cells = set()
        level_num += 1

        if cell_id in cell_visited or level_num > 500:
            return all_conn_cells

        all_conn_cells.add(cell_id)
        cell_visited.add(cell_id)
        conn_cells = set()

        for edge in cell_edges[cell_id]:
            cell_list = cell_adj[edge]
            for cid in cell_list:
                if cid == cell_id or cid in cell_visited:
                    continue
                normal = [ normals.GetComponent(cid,i) for i in range(3)]
                dp = sum([cell_normal[k]*normal[k] for k in range(3)])
                #print('[get_connected_cells] cid {0:d}  normal: {1:s}  dp: {2:g}'.format(cid, str(cell_normal), dp))
                if dp >= tol:
                    conn_cells.add(cid)
            #_for cid in cell_list
        #_for edge in cell_edges[cell_id]
        #print('[get_connected_cells] conn_cells: {0:s} '.format(str(conn_cells)))

        for cid in conn_cells:
            all_conn_cells.add(cid)
            new_conn_cells = self.get_connected_cells(cid, cell_normal, cell_adj, cell_edges, normals, cell_visited, level_num)
            #print('[get_connected_cells] new_conn_cells: {0:s} '.format(str(new_conn_cells)))
            for new_cid in new_conn_cells: 
                all_conn_cells.add(new_cid)

        #print('[get_connected_cells] all_conn_cells: {0:s} '.format(str(all_conn_cells)))
        return all_conn_cells

    def find_flat_regions(self):
        '''Find connected flat regions of the surface geometry.
        '''
        print('[surface] ========== find_flat_regions ==========')
        num_points = self.geometry.GetNumberOfPoints()
        num_cells = self.geometry.GetNumberOfCells()
        points = self.geometry.GetPoints()
        normals = self.geometry.GetCellData().GetArray('Normals')

        ## Build cell adjacency table.
        #
        cell_adj = defaultdict(set)
        cell_edges = defaultdict(set)

        for i in range(num_cells):
            #print('----- cell {0:d} -----'.format(i))
            cell = self.geometry.GetCell(i)
            cell_pids = cell.GetPointIds()
            num_edges = cell.GetNumberOfEdges()
            #print('[compute_faces] num_edges: {0:d}'.format(num_edges))
            #print('[compute_faces] cell_pids: {0:s}'.format(str(cell_pids)))
            cell_normal = [ normals.GetComponent(i,j) for j in range(3)]
            #print('[compute_faces] normal: {0:s}'.format(str(cell_normal)))
            for j in range(num_edges):
                edge = cell.GetEdge(j)
                edge_ids = edge.GetPointIds()
                pid1 = edge_ids.GetId(0)
                pid2 = edge_ids.GetId(1)
                if pid1 > pid2:
                    min_pid = pid2
                    max_pid = pid1
                else:
                    min_pid = pid1
                    max_pid = pid2
                cell_adj[(min_pid,max_pid)].add(i)
                cell_edges[i].add((min_pid,max_pid))
                #print('[compute_faces] edge: {0:d} {1:d}'.format(pid1, pid2))
            #_for j in range(num_edges):
        #_for i in range(num_cells)

        normal = 3*[0.0]
        cell_regions = defaultdict(set)
        cell_visited = set()

        ## Determine regions.
        #
        cell_count = 0
        level_num = 0
        regions = {}
        region_sizes = defaultdict(int)
        num_regions = 0
        max_region = 0
        max_region_size = 0

        for i in range(num_cells):
            if i in cell_visited:
                continue 
            #print('\n---------- cell {0:d} ----------'.format(i))
            cell_normal = [ normals.GetComponent(i,j) for j in range(3)]
            conn_cells = self.get_connected_cells(i, cell_normal, cell_adj, cell_edges, normals, cell_visited, level_num)
            if len(conn_cells) > 50:
                #print('\n---------- cell {0:d} ----------'.format(i))
                #print('conn_cells {0:d}  {1:s}'.format(len(conn_cells), str(conn_cells)))
                #show_region(renderer, surface, conn_cells)
                regions[i] = conn_cells 
                region_sizes[i] = len(conn_cells)
                if len(conn_cells) > max_region_size:
                    max_region_size = len(conn_cells)
                    max_region = i
                num_regions += 1
            cell_count += len(conn_cells)
            #_for edge in cell_edges[i]
        #_for i in range(num_cells)
        #print('[surface] cell_count: {0:d} '.format(cell_count))
        #print('[surface] max_region: {0:d} '.format(max_region))
        #print('[surface] max_region_size: {0:d} '.format(max_region_size))

        ## Store the four regions with max number of cells.
        region_count = 1
        self.flat_regions = []
        for rid in sorted(region_sizes, key=region_sizes.get, reverse=True):
            if region_count == 5:
               break
            region_count += 1
            self.flat_regions.append(Region(self, regions[rid]))

        print('[surface] ---------- regions ----------')
        for i,region in enumerate(self.flat_regions):
            num_cells = len(region.cell_ids)
            area = region.area
            max_r = region.max_radius
            if i == 0:
                color = [1,0,0]
            elif i == 1:
                color = [0,1,0]
            elif i == 2:
                color = [0,0,1]
            if i < 3:
               region.show(color)
               print('[surface] region: {0:d}  num_cells: {1:d}  area: {2:g}  max_rad {3:g}  color: {4:s}'.format(i, num_cells, area, max_r, str(color))) 


