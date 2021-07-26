#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name
import math

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Image(object):

    def __init__(self, params):
        self.params = params
        self.volume = None
        self.graphics = None
        self.paths = None
        self.logger = logging.getLogger(get_logger_name())
        self.greyscale_lut = None
        self.hue_lut = None 
        self.sat_lut = None
        self.colors = vtk.vtkNamedColors()

    def create_greyscale_lut(self, scalar_range):
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetRange(imin, imax) # image intensity range
        table.SetValueRange(0.0, 1.0) # from black to white
        table.SetSaturationRange(0.0, 0.0) # no color saturation
        table.SetRampToLinear()
        table.Build()
        self.greyscale_lut = table

    def create_hue_lut(self, scalar_range):
        ''' create a lookup table that consists of the full hue circle (from HSV).
        '''
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(imin, imax)
        table.SetHueRange(0, 1)
        table.SetSaturationRange(1, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.hue_lut = table

    def create_sat_lut(self, scalar_range):
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(imin, imax)
        table.SetHueRange(.6, .6)
        table.SetSaturationRange(0, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.sat_lut = table

    def read_volume(self, header):
        '''Read in a 3D image volume.
        '''
        filename, file_extension = path.splitext(self.params.image_file_name)
        reader = None
        if file_extension == ".vti":
            reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(self.params.image_file_name)
        reader.Update()
        self.volume = reader.GetOutput()

        self.extent = self.volume.GetExtent()
        self.width = self.extent[1] - self.extent[0]
        self.height = self.extent[3] - self.extent[2]
        self.depth = self.extent[5] - self.extent[4]
        self.scalar_range = self.volume.GetScalarRange()
        self.dimensions = self.volume.GetDimensions()
        self.spacing = self.volume.GetSpacing()
        self.origin = self.volume.GetOrigin()
        self.bounds = self.volume.GetBounds()
        self.scalars = self.volume.GetPointData().GetScalars()

        # Transform the image.
        #vtkImageChangeInformation(

        self.create_greyscale_lut((0,200))
        #self.create_greyscale_lut(self.scalar_range)
        self.create_hue_lut(self.scalar_range)
        self.create_sat_lut(self.scalar_range)

        '''
        image_point_data = imageDataVTK.GetPointData()
        image_data = vtkNumPy.vtk_to_numpy(image_point_data.GetArray(0))
        '''

        self.logger.info("Volume: ")
        self.logger.info("  dimensions: %s" % str(self.dimensions))
        self.logger.info("  extent: %s" % str(self.extent))
        self.logger.info("  spacing: %s" % str(self.spacing))
        self.logger.info("  origin: %s" % str(self.origin))
        self.logger.info("  bounds: %s" % str(self.bounds))
        self.logger.info("  width: %d" % self.width)
        self.logger.info("  height: %d" % self.height)
        self.logger.info("  depth: %d" % self.depth)
        self.logger.info("  scalar_range: %s" % str(self.scalar_range))

        self.graphics.add_sphere(self.origin, radius=0.2)

        x0, y0, z0 = self.origin
        xSpacing, ySpacing, zSpacing = self.spacing
        xMin, xMax, yMin, yMax, zMin, zMax = self.extent
        center = [x0 + 0.5*xSpacing * (xMax-1), y0 + 0.5*ySpacing * (yMax-1), z0 + 0.5*zSpacing * (zMax-1)]
        #self.graphics.add_sphere(center, radius=0.1, color=[1.0,0.0,0.0])

    def display_edges(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(self.volume)
        outline.Update()

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(outline.GetOutput())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(self.colors.GetColor3d("Black"))
        self.graphics.add_actor(actor)

    def display_axis_slice(self, axis, index):
        slice_colors = vtk.vtkImageMapToColors()
        slice_colors.SetInputData(self.volume)
        slice_colors.SetLookupTable(self.greyscale_lut)
        #slice_colors.SetLookupTable(self.hue_lut)
        #slice_colors.SetLookupTable(self.sat_lut)
        slice_colors.Update()

        slice = vtk.vtkImageActor()
        slice.GetMapper().SetInputData(slice_colors.GetOutput())

        if axis == 'i':
            imin = index 
            imax = index
            jmin = 0
            jmax = self.height
            kmin = 0
            kmax = self.depth

        elif axis == 'j':
            imin = 0
            imax = self.width
            jmin = index
            jmax = index 
            kmin = 0
            kmax = self.depth

        elif axis == 'k':
            imin = 0
            imax = self.width
            jmin = 0
            jmax = self.height
            kmin = index
            kmax = index 

        slice.SetDisplayExtent(imin, imax, jmin,jmax, kmin,kmax);
        slice.ForceOpaqueOn()
        slice.PickableOff()
        self.graphics.add_actor(slice)

    def volume_render(self, scalar_range):
        i1 = scalar_range[0]
        i2 = scalar_range[1]
        i3 = scalar_range[2]
        volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
        volumeMapper.SetInputData(self.volume)

        # The color transfer function maps voxel intensities to colors.
        # It is modality-specific, and often anatomy-specific as well.
        # The goal is to one color for flesh (between 500 and 1000)
        # and another color for bone (1150 and over).
        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(i1,  1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(i2, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(i3, 1.0, 1.0, 0.9)

        # The opacity transfer function is used to control the opacity
        # of different tissue types.
        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0,    0.00);
        volumeScalarOpacity.AddPoint(i1,  0.15);
        volumeScalarOpacity.AddPoint(i2, 0.15);
        volumeScalarOpacity.AddPoint(i3, 0.85);

        # The gradient opacity function is used to decrease the opacity
        # in the "flat" regions of the volume while maintaining the opacity
        # at the boundaries between tissue types.  The gradient is measured
        # as the amount by which the intensity changes over unit distance.
        # For most medical data, the unit distance is 1mm.
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(90,  0.5)
        volumeGradientOpacity.AddPoint(100, 1.0)

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)

        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)
        self.graphics.renderer.AddViewProp(volume)

    def extract_slice_bad(self, origin, tangent, normal, binormal):
        '''
        I could never get this to work.
        '''
        print(" ")
        print("---------- Image Extract Slice ----------") 
        print("origin: " + str(origin))
        print("tangent: " + str(tangent))
        print("normal: " + str(normal))
        print("binormal: " + str(binormal))

        xform = vtk.vtkMatrix4x4()
        x0, y0, z0 = self.origin
        xSpacing, ySpacing, zSpacing = self.spacing 
        xMin, xMax, yMin, yMax, zMin, zMax = self.extent
        center = [x0 + 0.5*xSpacing*xMax, y0 + 0.5*ySpacing*yMax, z0 + 0.5*zSpacing*zMax]
        print("Center: " + str(center))
        '''
        center = origin

        axial = vtk.vtkMatrix4x4()
        axial.DeepCopy((1, 0, 0, center[0],
                        0, 1, 0, center[1],
                        0, 0, 1, center[2],
                        0, 0, 0,   1       ))

        axial.DeepCopy((1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1  ))
        '''

        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(self.volume)
        reslice.SetOutputDimensionality(2)

        #reslice.SetResliceAxes(axial)
        reslice.SetResliceAxesOrigin(origin)
        reslice.SetResliceAxesDirectionCosines(normal, binormal, tangent)

        reslice.SetInterpolationModeToLinear()
        reslice.SetOutputSpacing(xSpacing, ySpacing, zSpacing)
        reslice.SetOutputExtent(xMin, xMax-1, yMin, yMax-1, zMin, zMax-1)
        reslice.SetOutputOrigin(0.0, 0.0, 0.0)
        reslice.UpdateWholeExtent()

        reslice.Update()

        islice = reslice.GetOutput()
        print("Slice number of points: {0:d}".format(islice.GetNumberOfPoints()))
        print("Slice number of cells: {0:d}".format(islice.GetNumberOfCells()))
        print("Slice origin: {0:s}".format(str(islice.GetOrigin())))
        print("Slice extent: {0:s}".format(str(islice.GetExtent())))
        print("Slice scalar range: {0:s}".format(str(islice.GetScalarRange())))

        # Map the image through the lookup table
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(self.greyscale_lut)
        color.SetInputData(reslice.GetOutput())
        color.Update()

        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputData(color.GetOutput())
        actor.GetMapper().BorderOn() 
        self.graphics.add_actor(actor)

    def extract_slice_gut(self, origin, tangent, normal, binormal):
        '''
        This works but can't clip slice.
        '''
        print(" ")
        print("---------- Image Extract Slice ----------") 
        print("origin: " + str(origin))
        print("tangent: " + str(tangent))
        print("normal: " + str(normal))
        print("binormal: " + str(binormal))

        # Define the slice plane.
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(origin[0], origin[1], origin[2])
        slice_plane.SetNormal(tangent[0], tangent[1], tangent[2])

        ## Create a mapper that slice a 3D image with an abitrary slice plane 
        #  and draw the results on the screen. 
        #
        reslice_mapper = vtk.vtkImageResliceMapper() 
        reslice_mapper.SetInputData(self.volume) 
        reslice_mapper.SliceFacesCameraOff()
        reslice_mapper.SliceAtFocalPointOff()
        reslice_mapper.SetSlicePlane(slice_plane)
        reslice_mapper.Update()

        ## vtkImageSlice is used to represent an image in a 3D scene. 
        #
        image_slice = vtk.vtkImageSlice() 
        image_slice.SetMapper(reslice_mapper) 
        image_slice.Update()
        self.graphics.add_actor(image_slice)
        print("Image slice: ")
        bounds = 6*[0]
        image_slice.GetBounds(bounds)
        print("  Bounds: " + str(bounds))
        #print(str(image_slice))

        ## Show slice bounds.
        #
        imageBoundsCube = vtk.vtkCubeSource()
        imageBoundsCube.SetBounds(self.bounds)
        imageBoundsCube.Update()
        #
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(slice_plane);
        cutter.SetInputData(imageBoundsCube.GetOutput());
        cutter.Update()
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputData(cutter.GetOutput())
        #
        planeBorder = vtk.vtkActor()
        planeBorder.GetProperty().SetColor(1.0, 1.0, 0)
        planeBorder.GetProperty().SetOpacity(1.0)
        planeBorder.GetProperty().SetLighting(0)
        planeBorder.GetProperty().SetLineWidth(4)
        planeBorder.SetMapper(cutterMapper)
        self.graphics.add_actor(planeBorder)

    ################# duplicate sv code #######################

    def math_cross(self, cross, vecA, vecB):
        cross[0] = vecA[1]*vecB[2]-vecA[2]*vecB[1]
        cross[1] = vecA[2]*vecB[0]-vecA[0]*vecB[2]
        cross[2] = vecA[0]*vecB[1]-vecA[1]*vecB[0]

    def math_magnitude(self, vecA):
        return math.sqrt(self.math_dot(vecA,vecA))

    def math_dot(self, vecA, vecB):
        return vecA[0]*vecB[0]+vecA[1]*vecB[1]+vecA[2]*vecB[2]

    def math_radToDeg(self, rad):
        return rad*180.0/math.pi

    def math_angleBtw3DVectors(self, vecA, vecB):
        dot = self.math_dot(vecA, vecB)
        magA = self.math_magnitude(vecA)
        magB = self.math_magnitude(vecB)
        cosTheta = dot / (magA * magB)
        if cosTheta >= 1: 
            cosTheta = 1
        return math.acos(cosTheta)

    def GetvtkTransform(self, pos, nrm, xhat):
        zhat = [0,0,1]
        theta = self.math_radToDeg(self.math_angleBtw3DVectors(zhat,nrm));
        axis = 3*[0.0]
        self.math_cross(axis, zhat, nrm)

        tmpTr = vtk.vtkTransform()
        tmpTr.Identity()
        tmpTr.RotateWXYZ(theta,axis)

        tmpPt = vtk.vtkPoints()
        tmpPt.InsertNextPoint(1, 0, 0)

        tmpPd = vtk.vtkPolyData()
        tmpPd.SetPoints(tmpPt)

        tmpTf = vtk.vtkTransformPolyDataFilter()
        tmpTf.SetInputDataObject(tmpPd)
        tmpTf.SetTransform(tmpTr)
        tmpTf.Update()
        pt = 3*[0.0]
        tmpTf.GetOutput().GetPoint(0,pt)

        rot = self.math_radToDeg(self.math_angleBtw3DVectors(pt,xhat))
        x = 3*[0.0]
        self.math_cross(x, pt, xhat)
        d = self.math_dot(x,nrm)
        if d < 0.0:
            rot = -rot

        tr = vtk.vtkTransform()
        tr.Identity()
        tr.Translate(pos)
        tr.RotateWXYZ(rot,nrm)
        tr.RotateWXYZ(theta,axis)

        return tr

    def simple_transform(self, pos, tangent, normal, binormal, image_matrix, image_origin):

        a0 = 0; a1 = 1; a2 = 2
        a0 = 1; a1 = 2; a2 = 0
        a0 = 2; a1 = 0; a2 = 1

        matrix = vtk.vtkMatrix4x4()
        matrix.Identity()
        for i in range(3):
           #matrix.SetElement(a0, i, tangent[i])
           #matrix.SetElement(a1, i, normal[i])
           #matrix.SetElement(a2, i, binormal[i])
           matrix.SetElement(i, a0, tangent[i])
           matrix.SetElement(i, a1, normal[i])
           matrix.SetElement(i, a2, binormal[i])

        transform = vtk.vtkTransform()

        #transform.Translate(image_origin[0], image_origin[1], image_origin[2])

        #transform.Concatenate(image_matrix)

        transform.Translate(pos[0], pos[1], pos[2])
        transform.Concatenate(matrix)

        #transform.Translate(-image_origin[0], -image_origin[1], -image_origin[2])


        return transform

    def extract_slice(self, pos, tangent, normal, binormal):

        #pos = [-0.0399223191235301, -0.284711064270262, 4.690705437545292]
        #tangent = [-0.08980586, -0.25193598, -0.96356794]
        #normal = [ 0.,          0.96747723, -0.25295811]
        #binormal = [ 0.99595929, -0.02271712, -0.08688512]

        print(" ")
        print("---------- Image Extract Slice ----------") 
        print("pos: " + str(pos))
        print("tangent: " + str(tangent))
        print("normal: " + str(normal))
        print("binormal: " + str(binormal))

        image_matrix = vtk.vtkMatrix4x4()
        image_matrix.Identity()
        image_matrix.SetElement(1, 1, 0.0)
        image_matrix.SetElement(1, 2, 1.0)
        image_matrix.SetElement(2, 1, -1.0)
        image_matrix.SetElement(2, 2, 0.0)
        image_matrix.Invert()

        image_origin = [-19.600, -7.480, 17.050]

        image_transform = vtk.vtkTransform()
        image_transform.Identity()
        image_transform.Translate(image_origin[0], image_origin[1], image_origin[2])
        image_transform.Concatenate(image_matrix)
        image_transform.Translate(-image_origin[0], -image_origin[1], -image_origin[2])
        print("image_transform: ")
        print(str(image_transform))

        ## Show a plane at a path position.
        #
        slice_transform = self.simple_transform(pos, tangent, normal, binormal, image_matrix, image_origin)
        slice_transform = self.GetvtkTransform(pos, tangent, normal)
        print("slice_transform 1: ")
        print(str(slice_transform))

        slice_transform.PostMultiply()
        slice_transform.Concatenate(image_transform)
        print("slice_transform 2: ")
        print(str(slice_transform))

        plane_pos = pos
        plane_normal = normal
        plane_source = vtk.vtkPlaneSource()
        plane_source.SetCenter([0,0,0])
        plane_source.SetNormal([0,0,1])
        #plane_source.SetPoint1([10,0,0])
        #plane_source.SetPoint2([0,10,0])
        plane_source.SetXResolution(100)
        plane_source.SetYResolution(100)
        plane_source.Update()
        plane_pd = plane_source.GetOutput()

        xform_filter = vtk.vtkTransformPolyDataFilter()
        xform_filter.SetInputDataObject(plane_pd)
        xform_filter.SetTransform(slice_transform)
        xform_filter.Update()
        geom = xform_filter.GetOutput()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(geom)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(2)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        self.graphics.add_actor(actor)

        ## Extract slice usinig vtkImageReslice.
        slice_spacing = 0.078
        slice_size = 5.0
        slice_width = int(slice_size / slice_spacing)
        slice_height = int(slice_size / slice_spacing)
        pdimx = slice_width * slice_spacing
        pdimy = slice_height * slice_spacing
        slice_origin = 3*[0.0]
        slice_origin[0] = -0.5*pdimx
        slice_origin[1] = -0.5*pdimy
        slice_origin[2] = 0.0
     
        image_reslice = vtk.vtkImageReslice()
        image_reslice.SetInputDataObject(self.volume)
        image_reslice.SetResliceTransform(slice_transform)
        image_reslice.SetOutputSpacing(slice_spacing, slice_spacing, slice_spacing)
        image_reslice.SetOutputOrigin(slice_origin)
        image_reslice.SetOutputExtent(0, slice_width-1, 0, slice_height-1, 0, 0)
        image_reslice.InterpolateOn()
        image_reslice.Update()
        image_slice = image_reslice.GetOutput()
        print("image_slice: ")
        print(str(image_slice))

        writer = vtk.vtkXMLImageDataWriter()
        writer.SetFileName("slice-image.vti");
        writer.SetInputData(image_slice)
        writer.Write();


        ## Show plane transformed to image.
        '''
        xform_filter = vtk.vtkTransformPolyDataFilter()
        xform_filter.SetInputDataObject(geom)
        xform_filter.SetTransform(image_transform)
        xform_filter.Update()
        geom = xform_filter.GetOutput()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(geom)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(2)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        self.graphics.add_actor(actor)
        '''

        # Define the slice plane.
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(pos[0], pos[1], pos[2])
        slice_plane.SetNormal(tangent[0], tangent[1], tangent[2])
        #slice_plane.SetTransformation(transform)

        ## Show slice bounds.
        #
        imageBoundsCube = vtk.vtkCubeSource()
        imageBoundsCube.SetBounds(self.bounds)
        imageBoundsCube.Update()
        #
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(slice_plane);
        cutter.SetInputData(imageBoundsCube.GetOutput());
        cutter.Update()
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputData(cutter.GetOutput())
        #
        planeBorder = vtk.vtkActor()
        planeBorder.GetProperty().SetColor(1.0, 1.0, 0)
        planeBorder.GetProperty().SetOpacity(1.0)
        planeBorder.GetProperty().SetLighting(0)
        planeBorder.GetProperty().SetLineWidth(4)
        planeBorder.SetMapper(cutterMapper)
        #self.graphics.add_actor(planeBorder)

        ## Interpolate slice plane points.
        #
        xSpacing, ySpacing, zSpacing = self.spacing
        w = 40.0 * xSpacing
        num_u = 200
        num_v = 200
        u = normal
        v = binormal
        pt0 = pos - w*(u + v)
        print("pt0: " + str(pt0))
        du = 2*w / num_u
        dv = 2*w / num_v
        
        points = vtk.vtkPoints()
        for j in range(num_v):
            for i in range(num_u):
                pt = pt0 + i*du*u + j*dv*v
                #print("{0:d}  {1:d}  pt {2:s}".format(i, j, str(pt)))
                points.InsertNextPoint(pt[0], pt[1], pt[2])
        #_for j in range(num_v)

        ## Outline slice.
        pt1 = pt0 + 0*du*u + 0*dv*v
        pt2 = pt0 + 0*du*u + (num_v-1)*dv*v
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + (num_u-1)*du*u + (num_v-1)*dv*v
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + (num_u-1)*du*u + 0*dv*v
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + 0*du*u + 0*dv*v
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)

        pts_polydata = vtk.vtkPolyData()
        pts_polydata.SetPoints(points)

        probe = vtk.vtkProbeFilter()
        probe.SetSourceData(self.volume)
        probe.SetInputData(pts_polydata)
        probe.Update()

        data = probe.GetOutput().GetPointData().GetScalars()
        num_values = data.GetNumberOfTuples()
        values = vtk.vtkDoubleArray()
        values.SetNumberOfValues(num_values);
  
        print("Interpolated data:")
        for i in range(data.GetNumberOfTuples()):
            val = data.GetValue(i)
            values.SetValue(i, val);
            #print(val)

        ## Show interpolation points.
        vertexFilter = vtk.vtkVertexGlyphFilter()
        vertexFilter.SetInputData(pts_polydata)
        vertexFilter.Update()

        polydata = vtk.vtkPolyData()
        polydata.ShallowCopy(vertexFilter.GetOutput())
        polydata.GetPointData().SetScalars(values)
        print("Scalar range: " + str(polydata.GetScalarRange()))

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetLookupTable(self.greyscale_lut)
        mapper.SetScalarRange(polydata.GetScalarRange())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(2)
        #actor.GetProperty().SetColor(1.0, 1.0, 0.0)
        self.graphics.add_actor(actor)


    def extract_isosurface(self, value):
        mc = vtk.vtkMarchingCubes()
        mc.SetInputData(self.volume)
        mc.SetValue(0, value)
        mc.Update()

        strip = vtk.vtkStripper()
        strip.SetInputData(mc.GetOutput())
        strip.Update()

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(strip.GetOutput())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        #actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(self.colors.GetColor3d("DarkSalmon"))
        actor.GetProperty().SetOpacity(0.5)
        self.graphics.add_actor(actor)


