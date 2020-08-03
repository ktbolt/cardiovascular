# Objective: Generate simVascular paths, segmentations, models, meshes, and run preSolver, solver and post process data in a user friendly and efficient manner
#   -This will include boundary conditions (For now assume steady flow file)
# Application(s): Cylindrical Models with set boundary conditions (For Now)


#####################################################
#                     Func Def                      #
#####################################################

# Function to create path and make cylindrical control points
def makePath(pointsList, pathName, contourName, radius):
    # Shortcut for function call Path.pyPath(), needed when calling SimVascular functions
    p = Path.pyPath()

    # Initializing path
    p.NewObject(pathName)
    print('Path name: ' + pathName)

    # Adding each point from pointsList to created path
    for pathPoint in pointsList:
        p.AddPoint(pathPoint)

    # Adding path to repository
    p.CreatePath()

    # Importing created path from repository to the 'Paths' tab in GUI
    GUI.ImportPathFromRepos(pathName)
    GUI.ImportPathFromRepos(pathName,'Paths')

    # Initializing variables and creating segmentations (Default to circle)
    Contour.SetContourKernel('Circle')
    pointsLength = len(pointsList)
    contourNameList = [pathName + 'ct1', pathName + 'ct2']

    # Creating 2 control segmentations for caps of the cylinder --
    # Segment #1
    c = Contour.pyContour() #  Shortcut for function call Contour.pyContour(), needed when calling SimVascular functions
    c.NewObject(contourNameList[0], pathName, 0)
    c.SetCtrlPtsByRadius(pointsList[0], radius+1)
    c.Create()
    c.GetPolyData('1ctp')
    # Segment #2
    numTwo = p.GetPathPtsNum() # index at end of pointsList
    c2 = Contour.pyContour()
    c2.NewObject(contourNameList[1], pathName, numTwo-1)
    c2.SetCtrlPtsByRadius(pointsList[1], radius+1)
    c2.Create()
    c2.GetPolyData('2ctp')

    # Importing contours from repository to 'Segmentations' tab in GUI
    GUI.ImportContoursFromRepos(contourName, contourNameList, pathName, 'Segmentations')

    return
# end of makePath


# Function to create contour
def makeContour():
    # Creating data to loft solid
    numSegs = 60 # number of segments defaulted to 60
    Geom.SampleLoop('1ctp', numSegs, '1ctps')
    Geom.SampleLoop('2ctp', numSegs, '2ctps')
    cList = ['1ctps', '2ctps']

    # Aligning profile to allow for lofting, meshing etc.
    Geom.AlignProfile('1ctps', '2ctps', 'ct2psa', 0)

    # Declaring needed variables for lofting
    srcList = ['1ctps', '2ctps']
    objName ='loft'
    numSegsAlongLength = 12
    numPtsInLinearSampleAlongLength = 240 # Referenced elsewhere? In LoftSolid function? No other mention in scripting
    numLinearSegsAlongLength = 120
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1

    # Lofting solid using created values
    Geom.LoftSolid(srcList, objName, numSegs, numSegsAlongLength, numLinearSegsAlongLength, numModes, useFFT, useLinearSampleAlongLength)

    # Importing PolyData from solid to repository
    GUI.ImportPolyDataFromRepos('loft')

    # Adding caps to model
    VMTKUtils.Cap_with_ids('loft','fullLoft',0,0)

    # Shortcut for function call Solid.pySolidModel(), needed when calling SimVascular functions
    s1 = Solid.pySolidModel()

    # Creating model
    Solid.SetKernel('PolyData')
    s1.NewObject('cyl')
    s1.SetVtkPolyData('fullLoft')
    s1.GetBoundaryFaces(90)
    print("Creating model: \nFaceID found: " + str(s1.GetFaceIds()))
    s1.WriteNative(os.getcwd() + "/cylinder.vtp")
    GUI.ImportPolyDataFromRepos('fullLoft')
    print('Caps added to fullLoft')
# end of makeContour


# Function to generate mesh of model
def makeMesh():
    # Meshing object
    MeshObject.SetKernel('TetGen')
    msh = MeshObject.pyMeshObject()
    msh.NewObject('mesh')
    solidFn = os.getcwd() + '/cylinder.vtp'
    msh.LoadModel(solidFn)
    msh.NewMesh()
    msh.SetMeshOptions('SurfaceMeshFlag',[1])
    msh.SetMeshOptions('VolumeMeshFlag',[1])
    msh.SetMeshOptions('GlobalEdgeSize',[0.75])
    msh.SetMeshOptions('MeshWallFirst',[1])
    msh.GenerateMesh()
    fileName = os.getcwd() + "/cylinder.vtk"
    msh.WriteMesh(fileName)
    msh.GetUnstructuredGrid('Mesh')
    Repository.WriteVtkUnstructuredGrid("Mesh","ascii",fileName)
    GUI.ImportUnstructedGridFromRepos('Mesh')
    print('Mesh generated')
# end of makeMesh


# Function to run preSolver, solver, and begin post processing data
# Note!!!: preSolver, svsolver, and svpost function calls are unique to my system. Change them to reflect where they are stored on your system.
def runSPP():
    # Running preSolver from created model
    try:
        os.system('/usr/local/sv/svsolver/2019-01-19/svpre cylinderSim.svpre')
        print('Running preSolver')
    except:
        print('Unable to run preSolver')
    # Running solver
    try:
        os.system('/usr/local/sv/svsolver/2019-01-19/svsolver solver.inp ')
        print('Running solver')
    except:
        print('Unable to run solver')
    # Post processing data
    try:
        os.system('/usr/local/sv/svsolver/2019-01-19/svpost -start 30 -stop 60 -incr 10 -vtu testcyl -all')
        print('Post processing data')
    except:
        print('Unable to post process data')
    return
# end of runSPP


#####################################################
#                   Main                           #
####################################################

# Must import to use/call simVascular executables
import os
from sv import *

# Moving from root directory to directory of fileName.py
os.chdir('/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Simulations/cylSim') ########### Unique to my system. Change it to reflect where it is stored on your system.
print('Current directory: ' + os.getcwd())

# Declaring list of points to be used for path
listOfPoints = [[0.0,0.0,0.0],[10.0,10.0,10.0]]

# Creating path using makePath() function
makePath(listOfPoints, 'path1', 'segment1', 1.0)
# Creating contour using makeContour() function
makeContour()
# Creating mesh using makeMesh() function
makeMesh()
# Running solver, preSolver, and post process the data
runSPP()
