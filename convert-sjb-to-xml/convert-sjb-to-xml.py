#!/usr/bin/env python3
'''This program is used to convert an svSolver .sjb file to an svFSIplus solver input XML file.

   Note that not all of the solver solution parameters from the .sjb file solver_props section can be converted
   to svFSIplus solver input XML file parameters in the <LS type="NS"> section. Reasonable default values are
   set for these parameters. 

   Usage:

     convert-sjb-to-xml.py  --sjb-file=SJB_FILE  --mesh-directory=MESH_DIRECTORY  --flow-file=FLOW_FILE

   where

     SJB_FILE - The .sjb (job) XML file produced by the SimVascular Simulation Tool

     MESH_DIRECTORY - The directory containing the mesh surface files. This directory is created 
                      by the SimVascular Simulation Tool organized. 

                      For example:

                          mesh-complete
                          ├── mesh-complete.exterior.vtp
                          ├── mesh-complete.mesh.vtu
                          ├── mesh-surfaces
                          │   ├── cap_aorta.vtp
                          │   ├── cap_aorta_2.vtp

     FLOW_FILE - The .sjb (job) XML inlet flow file give by the "Original File" parameter (no file path). Note that the file
                 used by svSolver has a different format than the file used by svFSIplus; add the number of lines and the 
                 number of Fourier modes to the begining of the file.
       
     
'''
import argparse
import os 
import sys
import xml.etree.ElementTree as et
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

class Args(object):
    '''This class defines the command line arguments to the script.
    '''
    PREFIX = "--"
    FLOW_FILE = "flow_file"
    MESH_DIR = "mesh_directory"
    SJB_FILE= "sjb_file"

def cmd(name):
    '''Create an argparse command argument.
    '''
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    '''Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(cmd(Args.FLOW_FILE), help="The name of the inlet flow file.", required=True)
    parser.add_argument(cmd(Args.MESH_DIR), help="The name of the directory containing the mesh files.", required=True)
    parser.add_argument(cmd(Args.SJB_FILE), help="The name of the .sjb file containined the svSolver parameters.", required=True)
    return parser.parse_args(), parser.print_help

class CapProps(object):
    '''Parameters read from the sjb <cap_props> section.
    '''
    def __init__(self):
        self.name = None
        self.Analytic_Shape = None
        self.BC_Type = None
        self.C_Values = None
        self.Flow_Rate = None
        self.Fourier_Modes = None
        self.Original_File = None
        self.Period = None
        self.Point_Number = None
        self.Pressure = None
        self.R_Values = None
        self.Values = None

    def set_props(self, cap):
        '''Set the values of cap properties.
        '''
        set_props = {
          'Analytic Shape' : lambda value: setattr(self, 'Analytic_Shape', value),
          'BC Type'  : lambda value: setattr(self, 'BC_Type', value),
          'C Values'  : lambda value: setattr(self, 'C_Values', value),
          #'Flow Rate'  : lambda value: setattr(self, 'Flow_Rate', value),
          'Fourier Modes'  : lambda value: setattr(self, 'Fourier_Modes', value),
          'Original File'  : lambda value: setattr(self, 'Original_File', value),
          'Period'  : lambda value: setattr(self, 'Period', value),
          'Point Number'  : lambda value: setattr(self, 'Point_Number', value),
          'Pressure'  : lambda value: setattr(self, 'Pressure', value),
          'R Values'  : lambda value: setattr(self, 'R_Values', value),
          'Values'  : lambda value: setattr(self, 'Values', value),
        }

        self.name = cap.attrib['name']
        #print("[CapProps::set_props] ")
        #print("[CapProps::set_props] ---------- set cap properties ----------")

        #print("[CapProps::set_props] cap name: {0:s} ".format(self.name))
        for prop in cap.iter('prop'):
            name = prop.attrib['key']
            value = prop.attrib['value']
            #print("[get_cap_props]   {0:s}: {1:s}".format(name, value))
            try:
                set_props[name](value)
            except:
                pass


class SolverProps(object):
    '''Parameters read from the sjb <solver_props> section.
    '''
    def __init__(self):
        self.Backflow_stabilization_coefficient = None

        self.Maximum_Number_of_Iterations_for_svLS_NS_Solver = None
        self.Minimum_Required_Iterations = None

        self.Number_of_Krylov_Vectors_per_GMRES_Sweep = None
        self.Number_of_Solves_per_Left_hand_side_Formation = None
        self.Number_of_time_steps = None
        self.Number_of_Timesteps_between_Restarts = '100'

        self.Residual_Criteria = None
        self.svLS_Type = None

        self.Time_Step_Size = None
        self.Time_Integration_Rho_Infinity = None

        self.Tolerance_on_svLS_NS_Solver = None

    def set_props(self, job):
        '''Set the values of solver properties under the <solver_props> tag.
        '''
        props = {
          'Backflow Stabilization Coefficient' : lambda value: setattr(self, 'Backflow_stabilization_coefficient', value),
          'Maximum Number of Iterations for svLS NS Solver' : lambda value: setattr(self, 'Maximum_Number_of_Iterations_for_svLS_NS_Solver', value),
          'Minimum Required Iterations' : lambda value: setattr(self, 'Minimum_Required_Iterations', value),

          'Number of Krylov Vectors per GMRES Sweep' : lambda value: setattr(self, 'Number_of_Krylov_Vectors_per_GMRES_Sweep', value),
          'Number of Solves per Left-hand-side Formation' : lambda value: setattr(self, 'Number_of_Solves_per_Left_hand_side_Formation', value),
          'Number of Timesteps' : lambda value: setattr(self, 'Number_of_time_steps', value),
          'Number of Timesteps between Restarts' : lambda value: setattr(self, 'Number_of_Timesteps_between_Restarts', value),

          'Residual Criteria' : lambda value: setattr(self, 'Residual_Criteria', value),

          'svLS Type' : lambda value: setattr(self, 'svLS_Type', value),

          'Time Integration Rho Infinity' : lambda value: setattr(self, 'Time_Integration_Rho_Infinity', value),
          'Time Step Size' : lambda value: setattr(self, 'Time_Step_Size', value),
          'Tolerance on svLS NS Solver' : lambda value: setattr(self, 'Tolerance_on_svLS_NS_Solve', value),
        }
   
        for solver_props in job.iter('solver_props'):
            for prop in solver_props.iter('prop'):
                name = prop.attrib['key']
                value = prop.attrib['value']
                try:
                    props[name](value)
                except:
                    pass

class BasicProperties(object):
    '''Parameters read from the sjb <basic_props> section.
    '''
    def __init__(self):
        self.fluid_density = None
        self.fluid_viscosity = None
        self.ic_file = None
        self.initial_pressure = None
        self.initial_velocities = None

    def set_props(self, job):
        '''Set the values of basic properties under the <basic_props> tag.
        '''
        props = {
          'Fluid Density'      : lambda value: setattr(self, 'fluid_density', value),
          'Fluid Viscosity'    : lambda value: setattr(self, 'fluid_viscosity', value),
          'IC File'            : lambda value: setattr(self, 'ic_file', value),
          'Initial Pressure'   : lambda value: setattr(self, 'initial_pressure', value),
          'Initial Velocities' : lambda value: setattr(self, 'initial_velocities', [ v for v in value.split()]) 
        }

        for basic_props in job.iter('basic_props'):
            for prop in basic_props.iter('prop'):
                name = prop.attrib['key']
                value = prop.attrib['value']
                try:
                    props[name](value)
                except:
                    pass

class SolverParameters(object):
    '''The SolverParameters class reads in the sjb XML and stores the values of its parameters.
    '''
    class const(object):
      Dirichlet = 'Dirichlet'
      BoolFalse = 'false'
      Neumann = 'Neumann'
      Prescribed_Velocities = 'Prescribed Velocities'
      RCR = 'RCR'
      Resistance = 'Resistance'
      Steady = 'Steady'
      BoolTrue = 'true'
      Unsteady = 'Unsteady'

    def __init__(self):
        self.solver_props = SolverProps()
        self.basic_props = BasicProperties()
        self.cap_props = []
        self.wall_files = None
        self.flow_file = None

    def set_props(self, job):
        self.solver_props.set_props(job)
        self.basic_props.set_props(job)

        for xml_cap_props in job.iter('cap_props'):
            for xml_cap in xml_cap_props.iter('cap'):
                cap_prop = CapProps()
                cap_prop.set_props(xml_cap)
                self.cap_props.append(cap_prop)

    def get_surface_files(self, mesh_dir):
        '''Get the surface file names under the mesh-complete/mesh-surfaces directory.
        '''
        if not os.path.exists(mesh_dir):
            raise Exception("The mesh directory'" + mesh_dir + "' does not exist.")

        surfaces_dir = mesh_dir + '/mesh-surfaces'
        if not os.path.exists(surfaces_dir):
            raise Exception("The mesh surfaces directory'" + surfaces_dir + "' does not exist.")

        file_list = os.listdir(surfaces_dir)

        wall_files = [name for name in file_list if name.startswith('wall')]
        if len(wall_files) == 0:
            raise Exception("The mesh surfaces directory contains no filed of the form 'wall_'")

        self.wall_files = wall_files

    def read_sjb_file(self, file_name):
        '''Read a SimVascular Simulations .sjb XML file. 
        '''
        # Remove 'format' tag from xml file.
        f = open(file_name, "r")
        lines = f.readlines()
        new_lines = []
        for line in lines:
          if '<format' not in line:
            new_lines.append(line)

        # Create string from xml file and parse it.
        xml_string = "".join(new_lines)
 
        tree = et.ElementTree(et.fromstring(xml_string))
        #tree = et.parse(file_name)
        root = tree.getroot()

        # Iterate over job properties.
        for mitk_job in root.iter('mitk_job'):
            model_name = mitk_job.attrib['model_name']
            mesh_name = mitk_job.attrib['mesh_name']
            for job in mitk_job.iter('job'):
                self.set_props(job)

    def write_xml_file(self, file_name):
        '''Write svFSIplus solver input XML file.
        '''
        m_encoding = 'UTF-8'
        root = Element("svFSIFile")
        root.set("version", "0.1")
        self.add_general(root)
        self.add_mesh(root)
        self.add_equation(root)

        dom = xml.dom.minidom.parseString(et.tostring(root))
        xml_string = dom.toprettyxml()
        part1, part2 = xml_string.split('?>')

        with open(file_name, 'w') as xfile:
            xfile.write(part1 + 'encoding=\"{}\"?>\n'.format(m_encoding) + part2)
            xfile.close()

    def add_equation(self, xml_element):
        '''Add the <Add_equation> section.
        '''
        equation = SubElement(xml_element, 'Add_equation', {'type':'fluid'})
        basic_props = self.basic_props 
        solver_props = self.solver_props 

        SubElement(equation, 'Coupled').text = 'true'
        SubElement(equation, 'Min_iterations').text = solver_props.Minimum_Required_Iterations
        SubElement(equation, 'Max_iterations').text = '15'
        SubElement(equation, 'Tolerance').text = '1e-6'
        #SubElement(equation, 'Tolerance').text = solver_props.Tolerance_on_svLS_NS_Solve
        SubElement(equation, 'Backflow_stabilization_coefficient').text = solver_props.Backflow_stabilization_coefficient 

        SubElement(equation, 'Density').text = basic_props.fluid_density

        viscosity = SubElement(equation, 'Viscosity', {'model':'Constant'})
        SubElement(viscosity, 'Value').text = basic_props.fluid_viscosity

        self.add_linear_solver(equation)

        # Add the <Add_BC> sections.
        for cap in self.cap_props:
            self.add_boundary_condition(equation, cap)

        # Add the <Add_BC> sections for walls (not given in .sjb file).
        for wall in self.wall_files:
            self.add_wall_boundary_condition(equation, wall)

    def add_wall_boundary_condition(self, xml_element, wall_file_name):
        '''Add the <Add_BC> section for a wall.
        '''
        const = self.const
        base, extension = os.path.splitext(wall_file_name)
        boundary_condition = SubElement(xml_element, 'Add_BC', {'name':base})
        SubElement(boundary_condition, 'Type').text = const.Dirichlet
        SubElement(boundary_condition, 'Time_dependence').text = const.Steady
        SubElement(boundary_condition, 'Value').text = '0.0'

    def add_boundary_condition(self, xml_element, cap):
        '''Add the <Add_BC> section.
        '''
        boundary_condition = SubElement(xml_element, 'Add_BC', {'name':cap.name})
        const = self.const

        if cap.BC_Type == const.RCR:
            self.add_rcr_bc(boundary_condition, cap)

        elif cap.BC_Type == const.Resistance:
            self.add_resistance_bc(boundary_condition, cap)

        elif cap.BC_Type == const.Prescribed_Velocities:
            self.add_inflow_bc(boundary_condition, cap)

        else:
            raise Exception("The boundary condition type '" + cap.BC_Type + "' is not supported.")

    def add_inflow_bc(self, xml_element, cap):
        '''Add the <Add_BC> type = Prescribed Velocities section.
        '''
        shape_map = {'flat' : 'Flat', 
                     'parabolic' : 'Parabolic',
                     'plug' : 'Flat'};

        const = self.const
        SubElement(xml_element, 'Type').text = const.Dirichlet
        SubElement(xml_element, 'Time_dependence').text = const.Unsteady
        SubElement(xml_element, 'Temporal_values_file_path').text = self.flow_file
        #SubElement(xml_element, 'Temporal_values_file_path').text = cap.Original_File
        SubElement(xml_element, 'Profile').text = shape_map[cap.Analytic_Shape]

        SubElement(xml_element, 'Impose_flux').text = const.BoolTrue
        SubElement(xml_element, 'Zero_out_perimeter').text = const.BoolTrue

    def add_resistance_bc(self, xml_element, cap):
        '''Add the <Add_BC> type = Resistance section.
        '''
        const = self.const
        SubElement(xml_element, 'Type').text = const.Neumann
        SubElement(xml_element, 'Time_dependence').text = const.Resistance
        SubElement(xml_element, 'Value').text = '0.0'

    def add_rcr_bc(self, xml_element, cap):
        '''Add the <Add_BC> type = RCR section.
        '''
        const = self.const
        SubElement(xml_element, 'Type').text = const.Neumann
        SubElement(xml_element, 'Time_dependence').text = const.RCR

        rcr_xml_element = SubElement(xml_element, 'RCR_values')
        SubElement(rcr_xml_element, 'Capacitance').text = cap.C_Values

        r_values = cap.R_Values.split()
        SubElement(rcr_xml_element, 'Proximal_resistance').text = r_values[0]
        SubElement(rcr_xml_element, 'Distal_resistance').text = r_values[1]

        SubElement(rcr_xml_element, 'Distal_pressure').text = '0.0'
        SubElement(rcr_xml_element, 'Initial_pressure').text = '0.0'

    def add_linear_solver(self, xml_element):
        '''Add the <LS> section.
        '''
        solver_props = self.solver_props
        linear_solver = SubElement(xml_element, 'LS', {'type':solver_props.svLS_Type})
        linear_algebra = SubElement(linear_solver, 'Linear_algebra', {'type':'fsils'})
        SubElement(linear_algebra, 'Preconditioner').text = 'fsils'
        SubElement(linear_solver, 'Max_iterations').text = '20'
        SubElement(linear_solver, 'Tolerance').text = '1e-4'

        SubElement(linear_solver, 'NS_GM_max_iterations').text = '10'
        SubElement(linear_solver, 'NS_CG_max_iterations').text = '300'
        SubElement(linear_solver, 'NS_GM_tolerance').text = '1e-3'
        SubElement(linear_solver, 'NS_CG_tolerance').text = '1e-3'
        SubElement(linear_solver, 'Absolute_tolerance').text = '1e-12'
        SubElement(linear_solver, 'Krylov_space_dimension').text = '250'

    def add_mesh(self, root):
        '''Add the <Add_mesh> section.
        '''
        mesh_path = 'mesh-complete/'
        face_path = mesh_path + 'mesh-surfaces/'
        mesh = SubElement(root, 'Add_mesh', {'name':'mesh'})
        SubElement(mesh, 'Mesh_file_path').text = mesh_path + 'mesh-complete.mesh.vtu'

        # Add inlet/outlet faces.
        for cap in self.cap_props: 
            face = SubElement(mesh, 'Add_face', {'name':cap.name})
            SubElement(face, 'Face_file_path').text = face_path + cap.name + '.vtp'

        # Add walls. 
        for wall_file in self.wall_files: 
            base, extension = os.path.splitext(wall_file)
            face = SubElement(mesh, 'Add_face', {'name':base})
            SubElement(face, 'Face_file_path').text = face_path + wall_file 

    def add_general(self, root):
        '''Add the <GeneralSimulationParameters> section.
        '''
        GeneralSimulationParameters = SubElement(root, 'GeneralSimulationParameters')

        solver_props = self.solver_props

        SubElement(GeneralSimulationParameters, "Continue_previous_simulation").text = 'false'
        SubElement(GeneralSimulationParameters, "Number_of_spatial_dimensions").text = '3'

        SubElement(GeneralSimulationParameters, "Number_of_time_steps").text = solver_props.Number_of_time_steps
        SubElement(GeneralSimulationParameters, "Time_step_size").text = solver_props.Time_Step_Size
        SubElement(GeneralSimulationParameters, "Spectral_radius_of_infinite_time_step").text = solver_props.Time_Integration_Rho_Infinity

        # These parameters are not set in svSolver so use default values.
        #
        SubElement(GeneralSimulationParameters, "Searched_file_name_to_trigger_stop").text = 'STOP_SIM'

        SubElement(GeneralSimulationParameters, "Increment_in_saving_VTK_files").text = '10'
        SubElement(GeneralSimulationParameters, "Name_prefix_of_saved_VTK_files").text = 'result'
        SubElement(GeneralSimulationParameters, "Save_results_to_VTK_format").text = 'true'

        SubElement(GeneralSimulationParameters, "Increment_in_saving_restart_files").text = solver_props.Number_of_Timesteps_between_Restarts
        SubElement(GeneralSimulationParameters, "Start_saving_after_time_step").text = '1'

        SubElement(GeneralSimulationParameters, "Convert_BIN_to_VTK_format").text = 'false'


def main(file_name, mesh_dir, flow_file):

    # Create object to store solver paramerters.
    solver_parameters = SolverParameters()
    solver_parameters.flow_file = flow_file

    # Read a SV Simulations .sjb file. 
    solver_parameters.read_sjb_file(file_name)

    # Get surface file names.
    solver_parameters.get_surface_files(mesh_dir)

    solver_parameters.write_xml_file("svFSIplus.xml")

if __name__ == "__main__":
    args, print_help = parse_args()
    sjb_file = args.sjb_file
    mesh_dir = args.mesh_directory
    flow_file = args.flow_file

    if not os.path.exists(sjb_file):
        raise Exception("The sjb directory'" + sjb_file + "' does not exist.")

    if not os.path.exists(mesh_dir):
        raise Exception("The mesh directory'" + mesh_dir + "' does not exist.")

    if not os.path.exists(flow_file):
        raise Exception("The flow file '" + flow_file + "' does not exist.")

    main(sjb_file, mesh_dir, flow_file)

