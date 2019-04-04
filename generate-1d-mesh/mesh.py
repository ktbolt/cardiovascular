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

import numpy as np
import vtk.util.numpy_support as nps
from vmtk import vtkvmtk,vmtkscripts
from utils import SurfaceFileFormats, read_polydata, write_polydata

class Mesh(object):
    """ The Mesh class is used to encapsulate 1D mesh calculations.

    Attributes:
        path_elems (list[int]): Records the element indices for centerline ids.
    """

    class OutputFileNames(object):
        CONNECTIVITY_GROUP_ID = "connectivity_groupid.dat"

    class CellDataFields(object):
        CENTERLINE_IDS = "CenterlineIds" 
        BLANKING = "Blanking" 
        GROUP_IDS = "GroupIds" 
        TRACT_IDS = "TractIds"

    def __init__(self):
        self.centerlines = None
        self.logger = logging.getLogger(get_logger_name())

    def generate(self, params, centerlines):
        """ Generate a mesh.
        """
        self.centerlines = centerlines
        self.logger.info("Generate the 1D mesh ...")

        if not self.check_centerlines_data(centerlines):
            return False

        ## Get centerline data.
        fields = self.CellDataFields
        centerline_list = self.get_cell_data(fields.CENTERLINE_IDS)
        blank_list = self.get_cell_data(fields.BLANKING)
        group_list = self.get_cell_data(fields.GROUP_IDS)
        tract_list = self.get_cell_data(fields.TRACT_IDS)
        num_cells = centerlines.GetNumberOfCells()
        num_paths = centerline_list[-1]+1
        num_groups = max(group_list)+1
        self.logger.info("Number of cells: %d" % num_cells) 
        self.logger.info("Number of paths: %d" % num_paths) 
        self.logger.info("Number of groups: %d" % num_groups) 

        path_elems = self.get_path_elements(num_cells, num_paths, centerline_list)
        group_elems = self.get_group_elements(num_cells, num_groups, group_list)

        if not params.uniform_material:
            materials = self.generate_grouped_wall_properties(params, centerlines, num_groups)

        self.calculate_connectivity(params, centerlines, blank_list, centerline_list, group_list, tract_list, \
          num_paths, path_elems, num_groups, group_elems)
        

    def calculate_connectivity(self, params, centerlines, blank_list, centerline_list, group_list, tract_list, 
      num_paths, path_elems, num_groups, group_elems): 
        """ calculate connectivity.
        """

        ## Calculte segments lists and group segments.
        seg_list, group_seg, group_terminal = self.calculate_seg_lists(num_paths, num_groups, group_elems, blank_list)
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
            pathid1 = centerline_list[group_elems[pargroupid][0]]
            tractid1 = tract_list[group_elems[pargroupid][0]]

            # Find the corresponding element id in path_elems list and index+1 is 
            # the bifurcation index+2 is the child elem
            childelemid1 = path_elems[pathid1][tractid1+2]
            childgroupid1 = group_list[childelemid1]
            temp_conn.append(childgroupid1)

            # Find second child or third/fourth child.
            for j in range(len(group_elems[pargroupid])-1,0,-1):
                temppathid = centerline_list[group_elems[pargroupid][j]]
                temptractid = tract_list[group_elems[pargroupid][j]]
                tempelemid = path_elems[temppathid][temptractid+2]
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

        ## Write connectivity and other information.
        #
        output_dir = params.output_directory
        file_name = path.join(output_dir, self.OutputFileNames.CONNECTIVITY_GROUP_ID)
        with open(file_name, "w") as file:
            for i in range(0,len(connectivity)):
                for j in range(0, len(connectivity[i])):
                    file.write(str(connectivity[i][j])+" ")
                file.write("\n")

        """
        if len(outletfacename)!=0:
         #output outlet face names with the corresponding group id
         file = open("outletface_groupid.dat", "w")
         for i in range(0,num_group):
            if group_terminal[i]==1:
                tempelemid=group_elems[i][0]
                temppathid=centerline_list[tempelemid]
                file.write(outletfacename[temppathid]+" "+"GroupId "+str(i)+"\n")
         file.close()

        file = open("centerline_groupid.dat", "w")
        for i in range(0,num_path):
            file.write("Centerline "+str(i)+" "+str(group_list[path_elems[i][0]]))
            tmpgroupid=group_list[path_elems[i][0]]
            for j in range(1,len(path_elems[i])):
              if group_list[path_elems[i][j]]!=tmpgroupid:
                file.write(" "+str(group_list[path_elems[i][j]]))
                tmpgroupid=group_list[path_elems[i][j]]
            file.write("\n")
        file.close()
        """


    def calculate_seg_lists(self, num_paths, num_groups, group_elems, blank_list):
        """ Calculate segment list and group segments.
        """
        group_terminal = num_groups*[0]
        num_outlet = 0
        num_bif = 0
        tmp = len(group_elems[0])

        for i in range(num_groups):
            if blank_list[group_elems[i][0]] == 1:
                group_terminal[i] = 2
                num_bif = num_bif+1
            if (len(group_elems[i]) == 1) and (blank_list[group_elems[i][0]] != 1):
                group_terminal[i] = 1
                num_outlet = num_outlet+1

            if (len(group_elems[i]) > tmp) and (blank_list[group_elems[i][0]] != 1):
                tmp = len(group_elems[i])
                self.logger.warning("A group with id>0 contains more centerlines than group 0")
        #__for i in range(num_groups)

        if (tmp != len(group_elems[0])) or (tmp != num_outlet) or (num_paths != num_outlet):
            print( "warning: inlet group id is not 0 or number of centerlines is not equal to the number of outlets")
            print( "num_path=",num_path,"num_outlet=",num_outlet,"len(group_elems[0])=",len(group_elems[0]),"tmp=",tmp)
            exit()

        num_seg = num_groups - num_bif
        num_node = num_bif + num_outlet + 1

        seg_list = []
        group_seg = []

        for i in range(num_groups):
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

    def generate_grouped_wall_properties(self, params, centerlines, num_groups):
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

        for i in range(num_groups):
            group_thickness.append([])
            group_E.append([])

        for i in range(poly_data.GetNumberOfPoints()):
            group_thickness[group_ids[i]].append(float(thickness[i]))
            group_E[group_ids[i]].append(float(E[i]))

        materials = []
        for i in range(num_groups):
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

    def get_group_elements(self, num_cells, num_groups, group_list):
        """
        group_elems[i] records the element(line) indices for group id=i
        """
        group_elems = []
        for i in range(num_groups):
            group_elems.append([])

        for i in range(num_cells):
            group_elems[group_list[i]].append(i)
 
        return group_elems

    def get_path_elements(self, num_cells, num_paths, centerline_list):
        """
        path_elems[i] records the element(line) indices for centerline id=i.
        """
        path_elems = []

        for i in range(num_paths):
            path_elems.append([])

        for i in range(num_paths):
            for j in range(num_cells):
                if i == centerline_list[j]:
                    path_elems[i].append(j)
        #__for i in range(num_path)

        return path_elems 


    def check_centerlines_data(self, centerlines):
        """ Check that the centerline data contains all of the required fields.
        """
        field_names = [v for k,v in self.CellDataFields.__dict__.items() if not k.startswith('__')]
        for field in field_names: 
            if not centerlines.GetCellData().GetArray(field):
                self.logger.error("Centerlines do not contain the '%s' data field." % field) 
                return False
        #__for field in CellDataFields

        return True 

    def get_cell_data(self, field):
        """ Get the data for the given cell field names.
        """
        cell_data = self.centerlines.GetCellData().GetArray(field)
        return nps.vtk_to_numpy(cell_data)


