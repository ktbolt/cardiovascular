
"""
This script is used to test the SV 'contour' module.
"""

import sv
import sv_vis

import logging
import os

#---------------
# Visualization
#---------------
#
class Visualization(object):
    """
    The Visualization class is used to create a graphics window and display geometry.
    """
    def __init__(self):
        self.renderer, self.render_window = sv_vis.initRen('ContourTest')

    def add_geometry(self, name):
        actor = sv_vis.pRepos(self.renderer, name) 
        
    def show(self, time):
        sv_vis.interact(self.renderer, time)

#------
# Path 
#-------
#
class Path(object):
    """
    The Path class is used to store SV Path objects. 
    """
    def __init__(self, name, logger):
        self.name = name
        self.logger = logger
        self.sv_object = None
        self.control_points = None
        self.create_sv_object()

    def create_sv_object(self):
        """
        Create an SV Path object for testing contour functions.
        """
        self.logger.info("Create Path '{0:s}' ".format(self.name))
        try:
            dy = 1.0
            num_path_control_pts = 5;
            self.path_control_points = [ [0.0, i*dy, 0.0] for i in range(0,num_path_control_pts)]
            self.sv_object = sv.Path.pyPath()
            self.sv_object.NewObject(self.name)

            # Set path points.
            for i in range(0,len(self.path_control_points)):
                self.sv_object.AddPoint(self.path_control_points[i])

            # Create path geometry.
            self.sv_object.CreatePath()
            points = self.sv_object.GetPathPosPts()
            control_points = self.sv_object.GetControlPts()
            pos_pts = self.sv_object.GetPathPosPts()
        except Exception as error:
            self.logger.error("create_sv_object: {0}".format(error))

    def get_control_point(self, index):
        if (index > len(self.path_control_points)):
            index = 0
        return self.path_control_points[index]

#_class Path(object)

#---------
# Contour
#---------
#
class Contour(object):
    """
    The Contour class is used to test the SV Contour API functions.
    """
    def __init__(self, name, path, logger):
        self.name = name
        self.path = path
        self.path_index = None
        self.logger = logger
        #self.sv_object = None

    def get_area(self):
        self.logger.info("Testing Contour: Get area.")
        contour = self.sv_object 

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            area = contour.area()
            self.logger.info("   Area: {0:g}".format(area))
            self.logger.info("   Pass")
        except Exception as error:
            self.logger.info("   get_area: {0}".format(error))

    def get_perimeter(self):
        self.logger.info("Testing Contour: Get perimeter.")
        contour = self.sv_object

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            perimeter = contour.perimeter()
            self.logger.info("   Perimeter: {0:g}".format(perimeter))
            self.logger.info("   Pass")
        except Exception as error:
            self.logger.info("   get_perimeter: {0}".format(error))

    def get_center(self):
        self.logger.info("Testing Contour: Get center.")
        contour = self.sv_object

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            center = contour.center()
            self.logger.info("   Center: {0:s}".format(str(center)))
            self.logger.info("   Pass")
        except Exception as error:
            self.logger.info("   get_center: {0}".format(error))

    def create_smooth_contour(self, visualize=False):
        self.logger.info("Testing Contour: Create smooth contour.")
        contour = self.sv_object 

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            num_fourier = 5
            new_contour_name = self.name + "_smoothed"
            smoothed_contour = contour.create_smooth_contour(num_fourier, new_contour_name)
            self.logger.info("   Pass")
            if visualize:
                self.logger.info("   Visualize")
                smoothed_polydata_name = self.name + "_polydata"
                smoothed_contour.get_polydata(smoothed_polydata_name)
                visualization = Visualization()
                visualization.add_geometry(smoothed_polydata_name)
                visualization.show(1000)
        except Exception as error:
            self.logger.info("   create_smooth_contour: {0}".format(error))

    def get_polydata(self, visualize=False):
        self.logger.info("Testing Contour: Get polydata.")
        contour = self.sv_object 

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            polydata_name = self.name + "_polydata_get_polydata"
            contour.get_polydata(polydata_name)
            assert sv.Repository.Exists(polydata_name), "Polydata not added to repository."
            self.logger.info("   Pass")
            if visualize:
                self.logger.info("   Visualize")
                visualization = Visualization()
                visualization.add_geometry(polydata_name)
                visualization.show(1000)
        except Exception as error:
            self.logger.info("   get_polydata: {0}".format(error))
    #_def get_polydata(self)

#_class Contour(object)

#---------------
# CircleContour
#---------------
#
class CircleContour(Contour):
    """
    The CircleContour class is used to test the SV CircleContour API functions.
    """
    def __init__(self, name, path, path_index, radius, logger):
        Contour.__init__(self, name, path, logger)
        self.radius = radius 
        self.center = None 
        self.path = path
        self.path_index = path_index
        self.sv_object = None
        self.create_sv_circle_contour()

    def create_sv_circle_contour(self, suffix=""):
        self.logger.info("Create CircleContour '{0:s}' ".format(self.name))
        self.logger.info("  Radius: {0:g} ".format(self.radius))
        self.logger.info("  Path index: {0:d} ".format(self.path_index))
        try:
            sv.contour.set_contour_kernel('Circle')
            self.sv_object = sv.contour.Contour()
            self.sv_object.new_object(self.name+str(suffix), self.path.name, self.path_index)

            # Need to set controls points here or very bad things happen later (e.g. SV crashes).
            #self.center = self.path.get_control_point(self.path_index)
            self.center = 3*[0.0]
            self.sv_object.set_control_points_by_radius(self.center, self.radius)
            self.logger.info("  Center: {0:s} ".format(str(self.center)))
        except Exception as error:
            self.logger.error("   create_sv_circle_contour: {0}".format(error))

    def set_control_points_by_radius(self):
        """
        Test the set_control_points_by_radius function. This is a general function
        used by all of the Contour objects.
        """
        self.logger.info("Testing CircleContour: Set control points by radius")
        contour = self.sv_object 

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center, self.radius)
            contour.create()
            self.logger.info("   Contour center: {0:s}".format(str(contour.center()))) 
        except Exception as error:
            self.logger.info("   set_control_points_by_radius: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong number of arguments".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center)
        except Exception as error:
            self.logger.info("   set_control_points_by_radius: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong argument type".format(test_num))
        try:
            contour.set_control_points_by_radius(self.radius, self.center)
        except Exception as error:
            self.logger.info("   set_control_points_by_radius: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong type in center".format(test_num))
        try:
            contour.set_control_points_by_radius([1.0,0.0,'b'], 1.0)
        except Exception as error:
            self.logger.info("   set_control_points_by_radius: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong type for radius".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center, 'b')
        except Exception as error:
            self.logger.info("   set_control_points_by_radius: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Radius < 0.0".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center, -1.0)
        except Exception as error:
            self.logger.info("   set_control_points_by_radius: {0}".format(error))

    #_def set_control_points_by_radius(self)

    def set_control_points(self):
        """
        Test the Circle Contour set_control_pts function.
        """
        contour = self.sv_object 
        self.logger.info("\n")
        self.logger.info("Testing CircleContour: Set control points")

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            boundary = [x + 1.0 for x in self.center]
            control_pts = [self.center, boundary]
            self.logger.info("   Control points: {0:s}".format(str(control_pts))) 
            contour.set_control_points(control_pts)
            contour.create()
            self.logger.info("   Contour center: {0:s}".format(str(contour.center()))) 
        except Exception as error:
            self.logger.info("   set_control_point: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong number of arguments".format(test_num))
        try:
            contour.set_control_points(1.0, 2.0)
        except Exception as error:
            self.logger.info("   set_control_points: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong argument type".format(test_num))
        try:
            contour.set_control_points(1.0)
        except Exception as error:
            self.logger.info("   set_control_points: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong type in list of control points".format(test_num))
        try:
            contour.set_control_points([ [1.0,0.0,0.0], [-1, 'b', 'c'] ])
        except Exception as error:
            self.logger.info("   set_control_points: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong number of control points".format(test_num))
        try:
            contour.set_control_points([ [1.0,0.0,0.0] ])
        except Exception as error:
            self.logger.info("   set_control_points: {0}".format(error))

    #_def set_control_points(self)

#_class CircleContour(object)

#-------------
# ContourTest
#-------------
#
class ContourTest(object):
    """
    The ContourTest class is used to test the SV Contour API functions.
    """
    def __init__(self, name):
        self.name = name

        self.logger_name = "contour-test" 
        self.log_file_name = "contour-test.log" 
        self.logger = self.init_logging()

        # Create Path for testing.
        self.path = Path("test-path", self.logger)

    def init_logging(self, outputDir="./"):
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logFile = os.path.join(outputDir, self.log_file_name)
        file_handler = logging.FileHandler(logFile, mode="w")
        logger.addHandler(file_handler)
        file_handler.setFormatter(formatter)
        return logger

    def create_circle_contour(self, name="circle_contour_test"):
        """
        Create a default CircleContour object.
        """
        radius = 1.0
        path_index = 1
        contour = CircleContour(name, self.path, path_index, radius, self.logger)
        return contour 
    #_def create_circle_contour(self)

    def contour(self, visualize=False):
        """
        Test Contour functions.

        These are generic functions for all Contour types. Use a CircleContour 
        for these tests.
        """
        self.logger.info("==================================================")
        self.logger.info("                   Testing Contour                ")
        self.logger.info("==================================================")
        contour = self.create_circle_contour("generic_contour")

        # Tests.
        contour.create_smooth_contour(visualize)
        contour.get_polydata(visualize)
        contour.get_area()
        contour.get_perimeter()
        contour.get_center()

    def circle_contour(self, visualize=False):
        """
        Test CircleContour functions.
        """
        self.logger.info("==================================================")
        self.logger.info("              Testing CircleContour               ")
        self.logger.info("==================================================")
        contour = self.create_circle_contour("circle_contour")

        # Tests.
        contour.set_control_points_by_radius()
        contour.set_control_points()

    #_def circle_contour(self)


#_class ContourTest(object)

#help(sv.contour)

## Test contour functions.
#
contour_test = ContourTest("contour_test")
visualize = False
#visualize = True

# Test Contour object.
contour_test.contour(visualize)

# Test CircleContour object.
contour_test.circle_contour(visualize)

