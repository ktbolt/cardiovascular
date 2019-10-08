#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import vtk

def str2bool(value, raise_exc=False):
    if isinstance(value, str) or sys.version_info[0] < 3 and isinstance(value, basestring):
        value = value.lower()
        if value in _true_set:
            return True
        if value in _false_set:
            return False

    if raise_exc:
        raise ValueError('Expected "%s"' % '", "'.join(_true_set | _false_set))
    return None

class pointsToSurface():
    
    # Initialization of the object
    def __init__(self, path, file, write_out = True):
        
        self.path = path
        self.file = file
        
        # Remove ".mat" extensions from filename, for later use
        if (self.file.find(".mat") > -1):
            self.file = self.file[0:self.file.find(".mat")]
        
        self.points = vtk.vtkProgrammableSource()
        self.surface = vtk.vtkPolyData()

        # Function to read in point cloud
        def loadPoints():
            
            import scipy.io
            
            data_all = scipy.io.loadmat(self.path + self.file + ".mat");
            self.raw_points = data_all.get(self.file)
            
            p = vtk.vtkPoints()
            for i in range(self.raw_points.shape[0]):
                for j in range(self.raw_points.shape[1]):
                    x = self.raw_points[i,j,0]
                    y = self.raw_points[i,j,1]
                    z = self.raw_points[i,j,2]
                    p.InsertNextPoint(x, y, z)
            
            self.points.GetPolyDataOutput().SetPoints(p)
        
        self.points.SetExecuteMethod(loadPoints)
        self.surface = self.createSurface(self.points)
        
        # Write VTP file
        if (write_out) == True:
            self.writeVTP()
            
    # Construct the surface and create isosurface
    def createSurface(self, points):
            
        surf = vtk.vtkSurfaceReconstructionFilter()
        surf.SetInputConnection(points.GetOutputPort())
            
        cf = vtk.vtkContourFilter()
        cf.SetInputConnection(surf.GetOutputPort())
        cf.SetValue(0, 0.0)
    
        reverse = vtk.vtkReverseSense()
        reverse.SetInputConnection(cf.GetOutputPort())
        reverse.ReverseCellsOn()
        reverse.ReverseNormalsOn()
        reverse.Update()
            
        return reverse
    
    # Write created surface to a VTP file
    def writeVTP(self, filename = ""):
        
        if (filename == ""):
            filename = self.file
            
        wVTP = vtk.vtkXMLPolyDataWriter()
        
        wVTP.SetInputData(self.surface.GetOutput())
        wVTP.SetFileName(self.path + filename + '.vtp')
        
        wVTP.Write()
        
    # Plot the created surface in an interactive window
    def plotSurface(self):
        
        map = vtk.vtkPolyDataMapper()
        map.SetInputConnection(self.surface.GetOutputPort())
        map.ScalarVisibilityOff()
        
        surfaceActor = vtk.vtkActor()
        surfaceActor.SetMapper(map)
        surfaceActor.GetProperty().SetDiffuseColor(1.0000, 0.3882, 0.2784)
        surfaceActor.GetProperty().SetSpecularColor(1, 1, 1)
        surfaceActor.GetProperty().SetSpecular(.4)
        surfaceActor.GetProperty().SetSpecularPower(50)
        
        # Create the RenderWindow, Renderer and both Actors
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)
        
        # Add the actors to the renderer, set the background and size
        ren.AddActor(surfaceActor)
        ren.SetBackground(1, 1, 1)
        renWin.SetSize(400, 400)
        ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        ren.GetActiveCamera().SetPosition(1, 0, 0)
        ren.GetActiveCamera().SetViewUp(0, 0, 1)
        ren.ResetCamera()
        ren.GetActiveCamera().Azimuth(20)
        ren.GetActiveCamera().Elevation(30)
        ren.GetActiveCamera().Dolly(1.2)
        ren.ResetCameraClippingRange()
        
        iren.Initialize()
        renWin.Render()
        iren.Start()
        
    def extractCenterline(self):
        return self.raw_points.mean(axis=0)
        
# Make class usable from command line
if __name__ == "__main__":
    
    import argparse
    #from func_basic import str2bool
        
    # Add optional command line arguments
    parser = argparse.ArgumentParser(
             description='Create surface of a given point cloud (.mat file).')
    
    parser.add_argument('--path', type=str, nargs='?',
      help='String - Full path to the directory in which the file is located.')
    
    parser.add_argument('--file', type=str, nargs='?',
      help='String - Filename of the point cloud (.mat file).')
    
    parser.add_argument('--write', type=str2bool, nargs='?', default=True, 
      help='Boolean - Write a .vtp file of the created surface.')
    
    parser.add_argument('--plot', type=str2bool, nargs='?', default=True, 
      help='Boolean - Create an interactive plot of the surface.')
    
    args = parser.parse_args()
    
    p = 0
    f = 0
    
    if args.path:
        
        # If specified path inclused the .mat file, no filename is required
        if (args.path.find(".mat") > -1 ):
            
            idx = args.path.rfind("\\")
            p = args.path[:idx]
            f = args.path[(idx+1):]
            
        elif args.file:
            
            p = args.path
            if (args.file.find(".mat") > -1 ):
                f = args.file
            
    else:
        
        # If no path is specified, it is assumed the .mat file is in the same
        #   folder with the script
        import os 
        p = os.path.dirname(os.path.realpath(__file__))
        
        if (args.file):
            if (args.file.find(".mat") > -1 ):
                f = args.file
    
    # If no path and/or no filename was specified, raise an error
    if (p==0) or (f==0):
        
        print("Matlab data not found!")
        sys.exit()
    
    # Create the surface for a specified point cloud
    pts = pointsToSurface(p,f,args.write)
    
    # If specified, plot the created surface
    if (args.plot == True):
        pts.plotSurface()
