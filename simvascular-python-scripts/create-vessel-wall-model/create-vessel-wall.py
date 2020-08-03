''' This script is used to create a model of a vessel wall by performing a Boolean 
    subtract operation between models of the inner and outer vessel contours.

    The script reads two models from the PROJECT/Models directory. Set the 'project_dir' to the
    location of your project containing the models.
'''
import os, pwd
import sys
import sv
import sv_vis as vis

## Get current directory.
home_dir = pwd.getpwuid(os.getuid()).pw_dir
# Set the ''project_dir' to the location of your project containing the models.
project_dir = home_dir+os.path.sep+"/SimVascular/Demo"
model_dir = project_dir+os.path.sep+"Models"

# Set the solid modeling kernel.
sv.Solid.SetKernel('PolyData')

## Read inner aorta solid model.
inner_model_name = 'aorta-inner'
file_name = "/Users/parkerda/SimVascular/Demo/Models/aorta-inner.vtp"

if not os.path.exists(file_name):
    print("ERROR: File does not exist.")
    sys.exit(1)
print("File exists.")

solid = sv.Solid.pySolidModel()
solid.ReadNative(inner_model_name, model_dir+os.path.sep+inner_model_name+'.vtp')

## Read outer aorta solid model.
outer_model_name = 'aorta-outer'
solid = sv.Solid.pySolidModel()
solid.ReadNative(outer_model_name, model_dir+os.path.sep+outer_model_name+'.vtp')

## Subtract inner aorta from outer aorta.
wall_solid_name = 'subtract-aorta-inner-outer'
solid.Subtract(wall_solid_name, outer_model_name, inner_model_name)
solid.GetBoundaryFaces(80)
print ("Model face IDs: " + str(solid.GetFaceIds()))
wall_solid_name_pd = 'subtract-aorta-inner-outer_pd'
solid.GetPolyData(wall_solid_name_pd, 0.1)
solid.SetVtkPolyData(wall_solid_name_pd)
# Add the model to the 'Models' SV Data Manager.
sv.GUI.ImportPolyDataFromRepos(wall_solid_name_pd, 'Models')

## Write the wall model into the PROJECT/Models directory.
wall_model_name = 'aorta-wall'
solid.WriteNative(model_dir+os.path.sep+wall_model_name+'.vtp')

