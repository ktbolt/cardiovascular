
'''
This script removes the model caps. 
'''
import sv
import sv_vis
import os
import sys
import vtk
import math

def read_solid_model(model_name):
    '''
    Read in a solid model.
    '''
    solid_file_name = os.getcwd() + '/' + model_name + '.vtp'
    sv.Solid.SetKernel('PolyData')
    solid = sv.Solid.pySolidModel()
    solid.ReadNative(model_name, solid_file_name)
    #solid.GetBoundaryFaces(60)
    #solid.DeleteFaces([2,3])
    print ("Model face IDs: " + str(solid.GetFaceIds()))
    model_polydata_name = model_name + "_pd"
    solid.GetPolyData(model_polydata_name)
    model_actor = sv_vis.pRepos(renderer, model_polydata_name)[1]
    model_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    #sv_vis.polyDisplayWireframe(renderer, model_polydata)
    #sv_vis.polyDisplayPoints(renderer, model_polydata_name)

    return solid, model_polydata_name, solid_file_name 

## Create a render and window to display geometry.
renderer, render_window = sv_vis.initRen('mesh-mess')

## Read solid model.
#
# Assume the first id in 'face_ids' is the source, the rest
# are targets for the centerline calculation.
#
model_name = "aorta-outer"
model_name = "capped"
model_name = "aorta-small"

if model_name == "aorta-outer":
    edge_size = 0.4733
    face_ids = [2, 3]
    walls = [1]
#
elif model_name == "demo":
    face_ids = [2, 3, 4]
    walls = [1]

elif model_name == "aorta-small":
    edge_size = 0.4431
    face_ids = [2, 3]
    walls = [1]

elif model_name == "capped":
    edge_size = 0.4431
    face_ids = [2, 3]
    walls = [1]

solid, model_polydata_name, solid_file_name = read_solid_model(model_name)
print ("Model face IDs: " + str(solid.GetFaceIds()))


## Display the graphics.
sv_vis.interact(renderer, sys.maxsize)


