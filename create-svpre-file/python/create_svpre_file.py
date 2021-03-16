#!/usr/bin/env python
'''This program is used to create an svSolver .svpre file from a SV project Simulations .sjb file.
'''
import sys
import xml.etree.ElementTree as et

class SolverParameterBC(object):
    def __init__(self, name):
        self.name = name

        # Prescribed velocities bc.
        self.analytic_shape = None
        self.bc_type = None
        self.flip_normal = None
        self.flow_rate = None 
        self.fourier_modes = None
        self.original_file = None
        self.period = None
        self.point_number = None
        self.pressure_period = None
        self.pressure_scaling = None
        self.time_pressure = None
        self.values = None

        # Resistance bc.
        self.resistance_pressure = None
        self.resistance_values = None

        # RCR bc.
        self.rcr_c_values = None
        self.rcr_r_values = None
        self.rcr_values = None

class SolverParameters(object):
    def __init__(self):
        self.fluid_density = None
        self.fluid_viscosity = None
        self.ic_file = None
        self.initial_pressure = None
        self.initial_velocities = None

    def get_basic_props(self, job):
        '''Set the values of basic properties.
        '''
        set_props = {
          'Fluid Density'      : lambda value: setattr(self, 'fluid_density', float(value)),
          'Fluid Viscosity'    : lambda value: setattr(self, 'fluid_viscosity', float(value)),
          'IC File'            : lambda value: setattr(self, 'ic_file', value),
          'Initial Pressure'   : lambda value: setattr(self, 'initial_pressure', float(value)),
          'Initial Velocities' : lambda value: setattr(self, 'initial_velocities', [ float(v) for v in value.split()]) 
        }
          
        print("[get_basic_props] ---------- get basic properties ----------")
        for basic_props in job.iter('basic_props'):
            for prop in basic_props.iter('prop'):
                name = prop.attrib['key']
                value = prop.attrib['value']
                print("[get_basic_props] {0:s}: {1:s}".format(name, value))
                try:
                    set_props[name](value)
                except:
                    pass

        #print("[get_basic_props] Fluid density: {0:g}".format(self.fluid_density))
        #print("[get_basic_props] Initial velocities: {0:s}".format(str(self.initial_velocities)))

    def get_cap_props(self, job):
        '''Set the values of cap properties.
        '''
        set_props = {
          'Fluid Density'      : lambda value: setattr(self, 'fluid_density', float(value)),
        }

        print("[get_cap_props] ---------- get cap properties ----------")
        for cap_props in job.iter('cap_props'):
            #cap_name = cap_props.attrib['cap']
            for cap in cap_props.iter('cap'):
                cap_name = cap.attrib['name']
                print("[get_cap_props] cap name: {0:s} ".format(cap_name))
                for prop in cap.iter('prop'):
                    name = prop.attrib['key']
                    value = prop.attrib['value']
                    print("[get_cap_props]   {0:s}: {1:s}".format(name, value))
                    try:
                        set_props[name](value)
                    except:
                        pass


    def read_sjb_file(self, file_name):
        '''Read a SV Simulations .sjb file. 
        '''
        print("[read_sjb_file] File name: " + file_name)
        # Remove 'format' tag from xml file.
        f = open(file_name, "r")
        lines = f.readlines()
        new_lines = []
        for line in lines:
          if '<format' not in line:
            new_lines.append(line)

        # Create string from xml file and parse it.
        xml_string = "".join(new_lines)
        #print(xml_string)
 
        tree = et.ElementTree(et.fromstring(xml_string))
        #tree = et.parse(file_name)
        root = tree.getroot()
        print("[read_sjb_file] root tag: " + str(root.tag))

        for mitk_job in root.iter('mitk_job'):
            model_name = mitk_job.attrib['model_name']
            mesh_name = mitk_job.attrib['mesh_name']
            print("[read_sjb_file] model_name: " + model_name)
            print("[read_sjb_file] mesh_name: " + mesh_name)
            for job in mitk_job.iter('job'):
                print("[read_sjb_file] job: " + str(job))
                self.get_basic_props(job)
                self.get_cap_props(job)

def main():
    file_name = sys.argv[1]
    
    # Create object to store solver paramerters.
    solver_parameters = SolverParameters()

    # Read a SV Simulations .sjb file. 
    solver_parameters.read_sjb_file(file_name)

if __name__ == "__main__":
    main()

