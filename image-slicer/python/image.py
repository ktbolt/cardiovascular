#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Image(object):

    def __init__(self, params):
        self.params = params
        self.volume = None
        self.graphics = None
        self.logger = logging.getLogger(get_logger_name())
        self.greyscale_lut = None
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

    def read_volume(self):
        """ Read in a 3D image volume.
        """
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
        self.logger.info("  spacing: %s" % str(self.spacing))
        self.logger.info("  origin: %s" % str(self.origin))
        self.logger.info("  bounds: %s" % str(self.bounds))
        self.logger.info("  width: %d" % self.width)
        self.logger.info("  height: %d" % self.height)
        self.logger.info("  depth: %d" % self.depth)
        self.logger.info("  scalar_range: %s" % str(self.scalar_range))

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


