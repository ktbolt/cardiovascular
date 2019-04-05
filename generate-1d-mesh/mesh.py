#!/usr/bin/env python

"""
The module is used to create a 1D mesh from centerline geometry.

A 1D mesh is generated from the centerline geometry caculated from a closed polygonal surface.

A centerline consists of m cells, m=number of tract ids, the length of a cell/line is an approximation of a group. 
In Cell Data, lines are listed from 0 to m. For each line, the first number is the number of points for this line followed by 1st point to the last point.

a cell/element (named as LINE) is a segment/line that consists of n points.
"""

from os import path 
import logging
from manage import get_logger_name
from parameters import OutflowBoundaryConditionType 

import numpy as np
from vmtk import vtkvmtk,vmtkscripts
import vtk.util.numpy_support as nps
from vtk import vtkIdList
from utils import SurfaceFileFormats, read_polydata, write_polydata

class Mesh(object):
    """ The Mesh class is used to encapsulate 1D mesh calculations.

    Attributes:
        path_elems (list[int]): Records the element indices for centerline ids.
    """

    class OutputFileNames(object):
        CONNECTIVITY_GROUP_ID = "connectivity_groupid.dat"
        OUTLET_FACE_GROUP_ID = "outletface_groupid.dat"
        CENTERLINE_GROUP_ID = "centerline_groupid.dat"

    class CellDataFields(object):
        CENTERLINE_IDS = "CenterlineIds" 
        BLANKING = "Blanking" 
        GROUP_IDS = "GroupIds" 
        TRACT_IDS = "TractIds"

    class PointDataFields(object):
        MAX_INSCRIBED_RADIUS = "MaximumInscribedSphereRadius" 

    def __init__(self):
        self.centerlines = None
        self.logger = logging.getLogger(get_logger_name())

    def generate(self, params, centerlines):
        """ Generate a mesh.
        """
        self.centerlines = centerlines
        self.logger.info("Generate the 1D mesh ...")
        self.centerlines_geometry = centerlines.branch_geometry
        self.num_cells = None
        self.num_paths = None
        self.path_elems = None
        self.group_elems = None
        self.materials = None
        self.num_seg = None         
        self.seg_list = None         
        self.group_seg = None         
        self.group_terminal = None
        self.group_length = None 
        self.group_Ain =  None
        self.group_Aout = None 
        self.connectivity = None
        self.seg_connectivity = None
        self.seg_head = None
        self.seg_rear = None 
        self.nodes = None 
        self.user_outlet_path = None 
        self.bc_list = None
        self.user_outlet_names = None

        # if the geometry is in mm, convert to cgs
        self.lcoef = 0.1 
        self.Acoef = 0.01

        # Check that centerline geometry has the required data fields.
        if not self.check_centerlines_data():
            return False

        ## Get centerline data.
        fields = self.CellDataFields
        centerline_list = self.get_cell_data(fields.CENTERLINE_IDS)
        blank_list = self.get_cell_data(fields.BLANKING)
        group_list = self.get_cell_data(fields.GROUP_IDS)
        tract_list = self.get_cell_data(fields.TRACT_IDS)
        self.num_cells = self.centerlines_geometry.GetNumberOfCells()
        self.num_paths = centerline_list[-1]+1
        self.num_groups = max(group_list)+1
        self.logger.info("Number of cells: %d" % self.num_cells) 
        self.logger.info("Number of paths: %d" % self.num_paths) 
        self.logger.info("Number of groups: %d" % self.num_groups) 

        self.get_path_elements(centerline_list)
        self.get_group_elements(group_list)

        if not params.uniform_bc:
            self.get_variable_outflow_bcs(params)

        if not params.uniform_material:
            materials = self.generate_grouped_wall_properties(params)

        self.calculate_connectivity(params, blank_list, centerline_list, group_list, tract_list)

        self.calculate_seg_lengths(centerline_list, group_list, tract_list)

        self.calculate_node_coordinates(centerline_list, group_list, tract_list)

        if params.reorganize_seqments:
            self.reorganize_child_segments(centerline_list, group_list, tract_list)

        self.write_solver_file(params, centerline_list)

        self.write_results(params, centerline_list, group_list)
        

    def calculate_connectivity(self, params, blank_list, centerline_list, group_list, tract_list):
        """ calculate connectivity.
        """

        ## Calculate segments lists and group segments.
        seg_list, group_seg, group_terminal = self.calculate_seg_lists(blank_list)
        num_seg = len(seg_list)

        ## Create connectivity for segments.
        connectivity = []

        for i in range(num_seg):
            # If  groupid is not a terminal seg, then it is a parent seg.
            if group_terminal[seg_list[i]] != 0:
                continue
            pargroupid = seg_list[i]
            temp_conn = []
            temp_conn.append(pargroupid)
            print( "parent group id=",pargroupid)

            # For each non-terminal group, at least there are 2 paths going through 
            # the child segments and sharing this group.
            pathid1 = centerline_list[self.group_elems[pargroupid][0]]
            tractid1 = tract_list[self.group_elems[pargroupid][0]]

            # Find the corresponding element id in path_elems list and index+1 is 
            # the bifurcation index+2 is the child elem
            childelemid1 = self.path_elems[pathid1][tractid1+2]
            childgroupid1 = group_list[childelemid1]
            temp_conn.append(childgroupid1)

            # Find second child or third/fourth child.
            for j in range(len(self.group_elems[pargroupid])-1,0,-1):
                temppathid = centerline_list[self.group_elems[pargroupid][j]]
                temptractid = tract_list[self.group_elems[pargroupid][j]]
                tempelemid = self.path_elems[temppathid][temptractid+2]
                tempgroupid = group_list[tempelemid]
                repeat = 0
                for k in range (1,len(temp_conn)):
                    if tempgroupid == temp_conn[k]:
                        repeat = 1
                        break
                    if repeat == 0:
                       temp_conn.append(tempgroupid)
                #__for k in range (1,len(temp_conn))
            #__for j in range(len(group_elems[pargroupid])-1,0,-1)

            if len(temp_conn)>3:
                print( "there are more than 2 child segments for groupid=",pargroupid)

            connectivity.append(temp_conn)
        #__for i in range(num_seg)

        print( "connectivity in terms of groups",connectivity)

        seg_connectivity = []

        for i in range(len(connectivity)):
            temp_conn = []
            for j in range(len(connectivity[i])):
                temp_conn.append(group_seg[connectivity[i][j]])
            seg_connectivity.append(temp_conn)
        #__for i in range(len(connectivity))

        print("connectivity in terms of segments",seg_connectivity)

        self.num_seg = num_seg         
        self.seg_list = seg_list         
        self.group_seg = group_seg         
        self.group_terminal = group_terminal 
        self.connectivity = connectivity
        self.seg_connectivity = seg_connectivity

    def write_results(self, params, centerline_list, group_list):
        ## Write connectivity and other information.
        #
        output_dir = params.output_directory
        file_name = path.join(output_dir, self.OutputFileNames.CONNECTIVITY_GROUP_ID)
        with open(file_name, "w") as file:
            for i in range(0,len(self.connectivity)):
                for j in range(0, len(self.connectivity[i])):
                    file.write(str(self.connectivity[i][j])+" ")
                file.write("\n")
        #__with open(file_name, "w") as file


        ## Output outlet face names with the corresponding group id
        #
        if len(self.centerlines.outlet_face_names) != 0:
            outlet_face_names = self.centerlines.outlet_face_names
            file_name = path.join(output_dir, self.OutputFileNames.OUTLET_FACE_GROUP_ID)
            with open(file_name, "w") as file:
                for i in range(self.num_groups):
                    if self.group_terminal[i] == 1:
                        tempelemid = self.group_elems[i][0]
                        temppathid = centerline_list[tempelemid]
                        file.write(outlet_face_names[temppathid]+" "+"GroupId "+str(i)+"\n")
            #__with open(file_name, "w") as file
        #__if len(self.centerlines.self.outlet_face_names) ! = 0

        file_name = path.join(output_dir, self.OutputFileNames.CENTERLINE_GROUP_ID)
        with open(file_name, "w") as file:
            for i in range(self.num_paths):
                file.write("Centerline "+str(i)+" "+str(group_list[self.path_elems[i][0]]))
                tmpgroupid = group_list[self.path_elems[i][0]]
                for j in range(1,len(self.path_elems[i])):
                  if group_list[self.path_elems[i][j]] != tmpgroupid:
                    file.write(" "+str(group_list[self.path_elems[i][j]]))
                    tmpgroupid = group_list[self.path_elems[i][j]]
                file.write("\n")
            #__for i in range(0,num_paths)
        #__with open(file_name, "w") as file


    def calculate_seg_lists(self, blank_list):
        """ Calculate segment list and group segments.
        """
        group_terminal = self.num_groups*[0]
        num_outlet = 0
        num_bif = 0
        tmp = len(self.group_elems[0])

        for i in range(self.num_groups):
            if blank_list[self.group_elems[i][0]] == 1:
                group_terminal[i] = 2
                num_bif = num_bif+1
            if (len(self.group_elems[i]) == 1) and (blank_list[self.group_elems[i][0]] != 1):
                group_terminal[i] = 1
                num_outlet = num_outlet+1

            if (len(self.group_elems[i]) > tmp) and (blank_list[self.group_elems[i][0]] != 1):
                tmp = len(self.group_elems[i])
                self.logger.warning("A group with id>0 contains more centerlines than group 0")
        #__for i in range(num_groups)

        if (tmp != len(self.group_elems[0])) or (tmp != num_outlet) or (self.num_paths != num_outlet):
            print( "warning: inlet group id is not 0 or number of centerlines is not equal to the number of outlets")
            print( "num_path=",num_path,"num_outlet=",num_outlet,"len(group_elems[0])=",len(group_elems[0]),"tmp=",tmp)
            exit()

        num_seg = self.num_groups - num_bif
        num_node = num_bif + num_outlet + 1

        seg_list = []
        group_seg = []

        for i in range(self.num_groups):
            if group_terminal[i]!=2:
                seg_list.append(i)
                group_seg.append(len(seg_list)-1)
            else:
                group_seg.append(-1)

        print( "seg_list=",seg_list)
        print( "group_seg=",group_seg)

        if len(seg_list) != num_seg:
            print( "Error! length of seg_list is not equal to num_seg")
            exit()

        return seg_list, group_seg, group_terminal

    def generate_grouped_wall_properties(self, params):
        """ Generate grouped wall properties and write them to a file.
        """
        self.logger.info("Generate grouped wall properties ...") 
        self.logger.info("Read wall properties file: %s" % params.wall_properties_input_file) 
        poly_data = read_polydata(params.wall_properties_input_file)

        branch_clip = vmtkscripts.vmtkBranchClipper()
        branch_clip.Surface = poly_data
        branch_clip.Centerlines = centerlines
        branch_clip.Execute()
        surface = branch_clip.Surface

        self.logger.info("Write wall properties file: %s" % params.wall_properties_output_file) 
        write_polydata(params.wall_properties_output_file, surface)

        point_data = surface.GetPointData()
        thickness = nps.vtk_to_numpy(point_data.GetArray('thickness'))
        E = nps.vtk_to_numpy(point_data.GetArray('Young_Mod'))
        group_ids = nps.vtk_to_numpy(point_data.GetArray('GroupIds'))

        group_thickness = []
        group_E = []

        for i in range(self.num_groups):
            group_thickness.append([])
            group_E.append([])

        for i in range(poly_data.GetNumberOfPoints()):
            group_thickness[group_ids[i]].append(float(thickness[i]))
            group_E[group_ids[i]].append(float(E[i]))

        materials = []
        for i in range(self.num_groups):
            thickness_mean = 0.0
            E_mean = 0.0
            if len(group_thickness[i]) != 0:
                thickness_mean = np.mean(group_thickness[i])
                E_mean = np.mean(group_E[i])
            else:
                self.logger.info("Group %d is empty." % i) 
            materials.append([thickness_mean, E_mean])
        self.logger.info("Created %d materials." % len(materials)) 

        return materials

    def get_variable_outflow_bcs(self, params):
        """ Read in data for variable flow boundary conditions.
        """
        self.logger.info("Get variable outflow boundary conditions ...")
        user_outlet_path = []
        bc_list = []
        user_outlet_names = []
        outlet_face_names = self.centerlines.outlet_face_names
        bc_file = params.outflow_bc_file

        with open(bc_file) as file:
         if outflow_bc == params.OutflowBoundaryConditionType.RESISTANCE:
           for line in file:
            print ("line=",line)
            bc_list.append(float(line))
           if len(bc_list) != len(outlet_face_names):
            print( "The number of BC values =",len(bc_list)," is not consistant with the number of outlets=",len(outlet_face_names),"exit.")
            exit()

         if outflow_bc == params.OutflowBoundaryConditionType.RCR:
            keyword = file.readline()
           # print"keyword=",keyword
            while True:
              tmp = file.readline()
              if tmp == keyword:
               RCRval=[]
               RCRval.append(float(file.readline()))
               RCRval.append(float(file.readline()))
               RCRval.append(float(file.readline()))
               BClist.append(RCRval)
              if len(tmp) == 0:
             #   print "eof"
                break

        for i in range(num_path):
            for j in range(0,len(user_outlet_names)):
                if outlet_face_names[i] == user_outlet_names[j]:
                    user_outlet_path.append(j)
                    break
        #__for i in range(num_path)

        self.user_outlet_path = user_outlet_path 
        self.bc_list = bc_list
        self.user_outlet_names = user_outlet_names


    def get_group_elements(self, group_list):
        """
        group_elems[i] records the element(line) indices for group id=i
        """
        group_elems = []
        for i in range(self.num_groups):
            group_elems.append([])

        for i in range(self.num_cells):
            group_elems[group_list[i]].append(i)
 
        self.group_elems = group_elems

    def get_path_elements(self, centerline_list):
        """
        path_elems[i] records the element(line) indices for centerline id=i.
        """
        path_elems = []

        for i in range(self.num_paths):
            path_elems.append([])

        for i in range(self.num_paths):
            for j in range(self.num_cells):
                if i == centerline_list[j]:
                    path_elems[i].append(j)
        #__for i in range(num_path)

        self.path_elems = path_elems 

    def check_centerlines_data(self):
        """ Check that the centerline data contains all of the required fields.
        """
        field_names = [v for k,v in self.CellDataFields.__dict__.items() if not k.startswith('__')]
        for field in field_names: 
            if not self.centerlines_geometry.GetCellData().GetArray(field):
                self.logger.error("Centerlines do not contain the '%s' data field." % field) 
                return False
        #__for field in field_names

        field_names = [v for k,v in self.PointDataFields.__dict__.items() if not k.startswith('__')]
        for field in field_names: 
            if not self.centerlines_geometry.GetPointData().GetArray(field):
                self.logger.error("Centerlines do not contain the '%s' data field." % field) 
                return False
        #__for field in field_names

        return True 

    def get_cell_data(self, field):
        """ Get the data for the given cell field names.
        """
        cell_data = self.centerlines_geometry.GetCellData().GetArray(field)
        return nps.vtk_to_numpy(cell_data)


    def calculate_seg_lengths(self, centerline_list, group_list, tract_list):
        """ calculate seg length, Ain and Aout
        """
        num_groups = self.num_groups
        group_elems = self.group_elems
        group_terminal = self.group_terminal
        path_elems = self.path_elems
        num_seg = self.num_seg
        seg_list = self.seg_list
        cl_geom = self.centerlines_geometry

        group_length = []
        group_Ain = []
        group_Aout = []
        seg_head = []
        seg_rear = []

        # Get max inscribed sphere radius data.
        field_name = self.PointDataFields.MAX_INSCRIBED_RADIUS
        celldata = cl_geom.GetPointData().GetArray(field_name)
        points_maxR = nps.vtk_to_numpy(celldata)
        points = cl_geom.GetPoints()

        for i in range(num_groups):
            tmpl = 0.0
            tmpAin = 0.0
            tmpAout = 0.0

            for j in range(0,len(group_elems[i])):
                ids = vtkIdList()
                cl_geom.GetCellPoints(group_elems[i][j],ids)
                num_ids = ids.GetNumberOfIds()
                tmpAin = tmpAin + np.pi*points_maxR[ids.GetId(0)]**2
                tmpAout = tmpAout + np.pi*points_maxR[ids.GetId(num_ids-1)]**2
                for k in range(0,num_ids-2):
                    id1 = ids.GetId(k)
                    id2 = ids.GetId(k+1)
                    pt1 = np.array([points.GetPoint(id1)[0], points.GetPoint(id1)[1], points.GetPoint(id1)[2]])
                    pt2 = np.array([points.GetPoint(id2)[0], points.GetPoint(id2)[1], points.GetPoint(id2)[2]])
                    tmpl = tmpl + np.linalg.norm(pt2-pt1)
                #__for k in range(0,num_ids-2)
            #__for j in range(0,len(group_elems[i]))
         
            tmpl = self.lcoef * tmpl/len(group_elems[i])
            tmpAin = self.Acoef * tmpAin/len(group_elems[i])
            tmpAout = self.Acoef * tmpAout/len(group_elems[i])
 
            if (tmpAin < tmpAout) and (group_terminal[i] != 2):
                print("warning! Ain<Aout in group id = ",i)
                print("set Ain = Aout")
                tmpAin = tmpAout

            # For bifurcation group, approximate as a straight uniform cylinder.
            if group_terminal[i]  == 2:
                tmpAin = (tmpAin+tmpAout)/2.0
                tmpAout = tmpAin

            print( "group id = ",i,"averaged length = ", tmpl,"averaged Ain and Aout",tmpAin,tmpAout)
            group_length.append(tmpl)
            group_Ain.append(tmpAin)
            group_Aout.append(tmpAout)
        #__for i in range(num_groups)

        # Modify seg length, add bifurcation group length to the parent group.
        for i in range(num_seg):
            if group_terminal[seg_list[i]] != 1:
                pargroupid = seg_list[i]
                pathid1 = centerline_list[group_elems[pargroupid][0]]
                tractid1 = tract_list[group_elems[pargroupid][0]]
                # Find the bifurcation group.
                bifelem = path_elems[pathid1][tractid1+1]
                bifgroupid = group_list[bifelem]
                # Add the bifurcation group length to the parent group.
                print("biflength ",group_length[bifgroupid],"ratio to parent group length",group_length[bifgroupid]/group_length[pargroupid])
                group_length[pargroupid] = group_length[pargroupid]+group_length[bifgroupid]
            #__if group_terminal[seg_list[i]]!=1

        #__for i in range(num_seg)

        self.group_length = group_length
        self.group_Ain = group_Ain
        self.group_Aout = group_Aout

    def calculate_node_coordinates(self, centerline_list, group_list, tract_list):
        """ get node coordinates 
        """
        num_groups = self.num_groups
        group_elems = self.group_elems
        group_terminal = self.group_terminal
        path_elems = self.path_elems
        num_seg = self.num_seg
        seg_list = self.seg_list
        cl_geom = self.centerlines_geometry
        points = cl_geom.GetPoints()

        nodes = []
        ## Parent group id for node(i).
        grouprearnodeid = []
        ids = vtkIdList()
        cl_geom.GetCellPoints(0,ids)
        id1 = ids.GetId(0)
        nodes.append(points.GetPoint(id1))

        for i in range(num_groups):
          if group_terminal[i] == 0 or group_terminal[i] == 1:
             tempelemid = group_elems[i][0]
             cl_geom.GetCellPoints(tempelemid,ids)
             num_ids = ids.GetNumberOfIds()
             id1 = ids.GetId(num_ids-1)
             nodes.append(points.GetPoint(id1))
             grouprearnodeid.append(len(nodes)-1)
          else:
             # bifurcation group doesn't get a node id, use nodeid = -1 
             grouprearnodeid.append(-1)
        #__for i in range(num_groups)
        print ("number of nodes =  ",len(nodes))
        print ("group rear node id", grouprearnodeid     )
        seg_head = []
        seg_rear = []

        for i in range(num_seg):
            tempgroupid = seg_list[i]
            if tempgroupid == 0:
                 seg_head.append(0)
            else:
                 tempelemid = group_elems[tempgroupid][0]
                 temptractid = tract_list[tempelemid]
                 temppathid = centerline_list[tempelemid]
                 tempelemid = path_elems[temppathid][temptractid-2]
                 seg_head.append(grouprearnodeid[group_list[tempelemid]])
            seg_rear.append(grouprearnodeid[tempgroupid])
        #_for i in range(0,num_seg)


        print( "seg_head", seg_head)
        print( "seg_rear", seg_rear)

        self.seg_head = seg_head 
        self.seg_rear = seg_rear
        self.nodes = nodes


    def reorganize_child_segments(self, centerline_list, group_list, tract_list):
        """ Reorgazie child segments when ireorgseg==1 and the number of child segments>3.
        """
        num_groups = self.num_groups
        group_elems = self.group_elems
        group_terminal = self.group_terminal
        path_elems = self.path_elems
        num_seg = self.num_seg
        seg_list = self.seg_list
        seg_connectivity = self.seg_connectivity
        cl_geom = self.centerlines_geometry
        points = cl_geom.GetPoints()

        print ("seg list: ",len(seg_list))
        i = 0

        while i < len(seg_connectivity):
           if len(seg_connectivity[i])>4:
              print ("reorganize seg connectivity = ",seg_connectivity[i])
              parsegid = seg_connectivity[i][0]
              pargroupid = seg_list[parsegid]
              num_child = len(seg_connectivity[i])-1
              pathid1 = centerline_list[group_elems[pargroupid][0]]
              tractid1 = tract_list[group_elems[pargroupid][0]]
              # Find the bifurcation group
              bifelem = path_elems[pathid1][tractid1+1]
              bifgroupid = group_list[bifelem]
              bifl = group_length[bifgroupid]
              dl = bifl/(num_child-2)
              childsegs = []
              childsegs.extend(seg_connectivity[i][1:])
              #prevously add bif group length to the par group length
              group_length[pargroupid] = group_length[pargroupid]-bifl
              
              ids = vtkIdList()
              cl_geom.GetCellPoints(group_elems[pargroupid][0],ids)
              num_ids = ids.GetNumberOfIds()
              id1 = ids.GetId(num_ids-1) #last node for par seg
              pt1 = np.array([cl_geom.GetPoints().GetPoint(id1)[0],cl_geom.GetPoints().GetPoint(id1)[1],cl_geom.GetPoints().GetPoint(id1)[2]])
              childseg_dist = []

              # Sort child segments based on the distance to the parent segment, and add extra 
              # segments along the bifurcation segments instead of connecting all n child segments to 1 outlet
              for j in range(0, len(childsegs)):
                  childgroupid1 = seg_list[childsegs[j]]
                  ids = vtkIdList()
                  cl_geom.GetCellPoints(group_elems[childgroupid1][0],ids)
                  id2 = ids.GetId(0) # first node in each child seg
                  pt2 = np.array([points.GetPoint(id2)[0], points.GetPoint(id2)[1], points.GetPoint(id2)[2]])
                  childseg_dist.append(np.linalg.norm(pt2-pt1))
              #__for j in range(0, len(childsegs))

              print ("childsegs = ",childsegs)
              print ("dist = ",childseg_dist)
              dist_order = np.argsort(childseg_dist)
              print ("order = ",dist_order)

              # define bif group starting point and tangential vector
              ids = vtkIdList()
              cl_geom.GetCellPoints(group_elems[bifgroupid][0],ids)
              num_ids = ids.GetNumberOfIds()
              id1 = ids.GetId(0) 
              pt1 = np.array([points.GetPoint(id1)[0], points.GetPoint(id1)[1], points.GetPoint(id1)[2]])
              id2 = ids.GetId(int(num_ids/2)) 
              pt2 = np.array([points.GetPoint(id2)[0], points.GetPoint(id2)[1], points().GetPoint(id2)[2]])
              v = pt2-pt1
              v = v/np.linalg.norm(v)
             
              first_new_seg = len(seg_list)
              parrearnodeid = seg_rear[parsegid]
              if len(seg_list) != len(seg_head) or len(seg_list) != len(seg_rear):
                  print ("Something wrong! length of seg_list ! =  length seg_head/seg_rear")

              # Split the bif group into n-2 pieces and change the corresponding group length.
              for j in range(0,num_child-2):
                seg_list.append(bifgroupid)
                # Add rear node for each new seg.
                pt2 = pt1+v*dl
                nodes.append([pt2[0],pt2[1],pt2[2]])
                seg_rear.append(len(nodes)-1)
                seg_head.append(parrearnodeid)
                pt1 = pt2
                parrearnodeid = len(nodes)-1
              #__for j in range(0,num_child-2)

              # modify the group length. the group is splitted into n-2 segments, the length represents the segment length now.
              group_length[bifgroupid] = group_length[bifgroupid]/(num_child-2)

              #delete original connectivity with >3 child segments, add new segments splitted from the bif group to the connectivity and connect to child segments
              del seg_connectivity[i]
              i = i-1
              temp_conn = np.zeros((1+num_child-2,3)).astype(int)
              temp_conn[0][0] = parsegid
              #add splitted segments to the parement seg position 
              for j in range(0,num_child-2):   
                temp_conn[j+1][0] = first_new_seg+j
              # add child segment ids to the temp_conn
              for j in range(0,num_child-2):
                temp_conn[j][1] = first_new_seg+j
                temp_conn[j][2] = childsegs[dist_order[j]]
              # add last two child segments to temp_conn      
              temp_conn[num_child-2][1] = childsegs[dist_order[num_child-2]]
              temp_conn[num_child-2][2] = childsegs[dist_order[num_child-1]]
              for j in range(0,num_child-1):
                seg_connectivity.append(temp_conn[j])

              #modify head nodes for child segments
              for j in range(0, num_child-2):
                sorted_child_index = dist_order[j]
                seg_head[childsegs[sorted_child_index]] = seg_head[first_new_seg+j]
             
              seg_head[childsegs[dist_order[num_child-2]]] = seg_rear[-1]
              seg_head[childsegs[dist_order[num_child-1]]] = seg_rear[-1]
           #__if len(seg_connectivity[i])>4

           i = i+1
        #__while i < len(seg_connectivity)

        print ("num_seg = ",num_seg)
        num_seg = len(seg_list)   
        print ("redefine num_seg = ",num_seg)


    def write_solver_file(self, params, centerline_list):
        """ Write an solver input file.
        """
        solver_file = params.solver_output_file
        model_name, sep, tail = solver_file.partition('.')

        # Open file
        #file = open(model_name + ".in", "w")
        file = open(solver_file, "w")
        
        # Write header
        file.write("# ================================\n")
        file.write("# " + model_name + " MODEL - UNITS IN CGS\n")
        file.write("# ================================\n\n")
          
        # Model Header
        file.write("# ==========\n")
        file.write("# MODEL CARD\n")
        file.write("# ==========\n")
        file.write("# - Name of the model (string)\n\n")
        file.write("MODEL " + model_name + " \n\n")

        # Node Header
        nodes = self.nodes
        lcoef = self.lcoef
        file.write("\n\n### DO NOT CHANGE THIS SECTION - generated automatically \n")
        file.write("#\n")
        file.write("# ==========\n")
        file.write("# NODE CARD\n")
        file.write("# ==========\n")
        file.write("# - Node Name (double)\n")
        file.write("# - Node X Coordinate (double)\n")
        file.write("# - Node Y Coordinate (double)\n")
        file.write("# - Node Z Coordinate (double)\n\n")
        
        for i in range(0,len(nodes)):
          file.write("NODE " + str(i) + " ".join(str(nodes[i][j]*lcoef) for j in range(3)) )
         
        # Joint Header
        file.write("\n\n\n### DO NOT CHANGE THIS SECTION - generated automatically \n#")
        file.write("# ==========\n")
        file.write("# JOINT CARD\n")
        file.write("# ==========\n")
        file.write("# - Joint Name (string)\n")
        file.write("# - Joint Node (double)\n")
        file.write("# - Joint Inlet Name (string)\n")
        file.write("# - Joint Outlet Name (string)\n\n")
        
        # JointInlet and JointOutlet Header
        file.write("\n### DO NOT CHANGE THIS SECTION - generated automatically \n#")
        file.write("# ================================\n")
        file.write("# JOINTINLET AND JOINTOUTLET CARDS\n")
        file.write("# ================================\n")
        file.write("# - Inlet/Outlet Name (string)\n")
        file.write("# - Total Number of segments (int)\n")
        file.write("# - List of segments (list of int)\n\n")            
        
        seg_connectivity = self.seg_connectivity
        seg_rear = self.seg_rear 

        for i in range(0,len(seg_connectivity)):
          pargroupid = seg_connectivity[i][0]
          file.write("JOINT J" + str(i) + " " + str(seg_rear[pargroupid]) + " IN" + str(i) + " OUT" + str(i) + "\n")
          file.write("JOINTINLET IN" + str(i) + " " + "1 " + str(seg_connectivity[i][0]) + "\n")
          file.write("JOINTOUTLET OUT" + str(i) + " " + str(len(seg_connectivity[i])-1))
          for j in range(1,len(seg_connectivity[i])): 
             file.write(" " + str(seg_connectivity[i][j]))
          file.write("\n\n")

          # Segment Header
        file.write("# ============")
        file.write("# SEGMENT CARD")
        file.write("# ============")
        file.write("# - Segment Name (string)")
        file.write("# - Segment ID (int)")
        file.write("# - Segment Length (double)")
        file.write("# - Total Finite Elements in Segment (int)")
        file.write("# - Segment Inlet Node (int)")
        file.write("# - Segment Outlet Node (int)")
        file.write("# - Segment Inlet Area (double)")
        file.write("# - Segment Outlet Area (double)")
        file.write("# - Segment Inflow Value (double)")
        file.write("# - Segment Material (string)")
        file.write("# - Type of Loss (string - 'NONE','STENOSIS','BRANCH_THROUGH_DIVIDING','BRANCH_SIDE_DIVIDING','BRANCH_THROUGH_CONVERGING',")
        file.write("#                          'BRANCH_SIDE_CONVERGING','BIFURCATION_BRANCH')")
        file.write("# - Branch Angle (double)")
        file.write("# - Upstream Segment ID (int)")
        file.write("# - Branch Segment ID (int)")
        file.write("# - Boundary Condition Type (string - 'NOBOUND','PRESSURE','AREA','FLOW','RESISTANCE','RESISTANCE_TIME','PRESSURE_WAVE',")
        file.write("#                                     'WAVE','RCR','CORONARY','IMPEDANCE','PULMONARY')")
        file.write("# - Data Table Name (string)\n\n") 
        
        num_seg = self.num_seg
        seg_list = self.seg_list
        seg_rear = self.seg_rear 
        seg_head = self.seg_head
        group_elems = self.group_elems 
        group_length = self.group_length
        group_terminal = self.group_terminal 
        group_Ain = self.group_Ain 
        group_Aout = self.group_Aout 
        uniform_bc = params.uniform_bc
        outflow_bc = params.outflow_bc_type
        uniform_material = params.uniform_material
        dx = params.dx 
        minnumfe = params.minnumfe
        inflow_file = params.inflow_file 
        timestep = params.timestep 
        numtimesteps = params.numtimesteps
        tincr = params.tincr 

        for i in range(0,num_seg):
           if uniform_material:
             matname = "MAT1"
           else:
             matname = "MAT_group"+str(seg_list[i])
           
           numfe = int(round(group_length[seg_list[i]]/dx))

           if numfe < minnumfe:
             numfe = minnumfe

           file.write("SEGMENT" + " " + "Group"+ str(seg_list[i])+"_Seg"+str(i) + " " + str(i) + " "+ str(group_length[seg_list[i]]) + " " + str(numfe) + " "+ str(seg_head[i]) + " " + str(seg_rear[i]) + " " + str(group_Ain[seg_list[i]])+ " " + str(group_Aout[seg_list[i]])+ " " +"0.0 "+ matname + " NONE 0.0 0 0 ")

           if group_terminal[seg_list[i]] == 1:
              if uniform_bc:
                file.write(outflow_bc+ " " + outflow_bc +"_1 \n")
                #print("###### bug: group_terminal[seg_list[i]] == 1")
              else:
                tempgroupid = seg_list[i]
                tempelemid = group_elems[tempgroupid][0]
                temppathid = centerline_list[tempelemid]
                file.write(outflow_bc+ " "+ outflow_bc +"_"+str(path2useroutlet[temppathid])+ " \n")
           else:
              file.write("NOBOUND NONE \n")   
        #__for i in range(0,num_seg)
        
        
        file.write("\n\n")
        if uniform_bc == 1:
           file.write("DATATABLE " + outflow_bc +"_1 LIST \n")
           file.write(" \n")
           file.write("ENDDATATABLE \n \n")
        else:
           if outflow_bc =="RCR":
            for i in range(0,num_path):
             file.write("DATATABLE " + outflow_bc +"_"+str(i)+" LIST \n")
             for j in range(0, len(BClist[i])):
              file.write("0.0 "+ str(BClist[i][j]) +" \n")
             file.write("ENDDATATABLE \n \n")
           if outflow_bc =="RESISTANCE":
            for i in range(0,num_path):
             file.write("DATATABLE " + outflow_bc +"_"+str(i)+" LIST \n")
             file.write("0.0 "+ str(BClist[i]) +" \n")
             file.write("ENDDATATABLE \n \n")   
        
        file.write("\n\n")
        file.write("DATATABLE INFLOW LIST \n")
        if len(inflow_file) == 0:
         file.write("Copy and paste inflow data here. \n")
        else:
           with open(inflow_file) as inflow:
             for line in inflow:
               file.write(line)
        file.write("ENDDATATABLE \n")  
        file.write("\n\n")
        
        # SolverOptions Header
        file.write("#  ==================\n# SOLVEROPTIONS CARD\n# ==================\n# - Solver Time Step (double), \n# - Steps Between Saves (int), \n# - Max Number of Steps (int)\n# - Number of quadrature points for finite elements (int), \n# - Name of Datatable for inlet conditions (string)\n# - Type of boundary condition (string - 'NOBOUND','PRESSURE','AREA','FLOW','RESISTANCE','RESISTANCE_TIME','PRESSURE_WAVE',\n#                                        'WAVE','RCR','CORONARY','IMPEDANCE','PULMONARY')\n# - Convergence tolerance (double), \n# - Formulation Type (int - 0 Advective, 1 Conservative), \n# - Stabilization (int - 0 No stabilization, 1 With stabilization)\n\n")
        file.write("SOLVEROPTIONS "+ str(timestep)+ " "+ str(tincr) +" "+ str(numtimesteps) + " 2 INFLOW FLOW 1.0e-5 1 1\n\n")
        
        
        
          # Material Header
        mattype = params.mattype
        density = params.density 
        viscosity = params.viscosity 
        c1 = params.c1 
        c2 = params.c2 
        c3 = params.c3 

        file.write("#  =============\n# MATERIAL CARD\n# =============\n# - Material Name (string)\n# - Material Type (string - 'LINEAR','OLUFSEN')\n# - Material Density (double)\n# - Material Viscosity (double)\n# - Material Exponent (double)\n# - Material Parameter 1 (double)\n# - Material Parameter 2 (double)\n# - Material Parameter 3 (double)\n\n")
        
        if uniform_material:
           file.write("MATERIAL MAT1 " + mattype+" " + str(density)+" "+str(viscosity)+" " + "0.0 1.0 "+str(c1)+" "+str(c2)+" "+str(c3)+ " \n")
        
        if not uniform_material:
           for i in range(0,num_seg):
             tmp = 4.0/3.0*matlist[seg_list[i]][0]*matlist[seg_list[i]][1]/math.sqrt((group_Ain[seg_list[i]]+group_Aout[seg_list[i]])/2/3.14)
             file.write("MATERIAL MAT_group"+str(seg_list[i])+ " " + mattype+" " + str(density)+" "+str(viscosity)+" " + "0.0 1.0 "+str(c1)+" "+str(c2)+" "+str(tmp)+ " \n") 
        
        
        # Output Header
        file.write("\n#  ============\n# OUTPUT CARD\n# ============\n#\n# 1. Output file format. The following output types are supported:\n#\t\tTEXT. The output of every segment is written in separate text files for the flow rate, pressure, area and Reynolds number. The rows contain output values at varying locations along the segment while columns contains results at various time instants.\n#\t\tVTK. The results for all time steps are plotted to a 3D-like model using the XML VTK file format.\n# 2. VTK export option. Two options are available for VTK file outputs:\n#\t\t0 - Multiple files (default). A separate file is written for each saved increment. A pvd file is also provided which contains the time information of the sequence. This is the best option to create animations.\n#\t\t1 - The results for all time steps are plotted to a single XML VTK file.\n\n")  

        # Output properties
        outputformat = params.outputformat
        file.write("OUTPUT "+outputformat)
        file.write("\n") 
        
        # Close file
        file.close()
        
