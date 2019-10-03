
"""
This script is used to test the SV 'contour' module.
"""

import sv
import sv_vis as vis

import logging
import os

class CircleContour(object):
    def __init__(self, name, logger):
        self.name = name
        self.logger = logger
        self.path_index = None
        self.radius = None
        self.center = None
        self.sv_contour_object = None

    def set_control_points_by_radius(self):
        """
        Test the Circle Contour set_control_points_by_radius function.
        """
        self.logger.info("Testing CircleContour: Set control points by radius")
        contour = self.sv_contour_object 

        test_num = 1
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center, self.radius)
            contour.create()
            self.logger.info("   Contour center: {0:s}".format(str(contour.Center()))) 
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong number of arguments".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center)
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong argument type".format(test_num))
        try:
            contour.set_control_points_by_radius(self.radius, self.center)
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong type in center".format(test_num))
        try:
            contour.set_control_points_by_radius([1.0,0.0,'b'], 1.0)
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong type for radius".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center, 'b')
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Radius < 0.0".format(test_num))
        try:
            contour.set_control_points_by_radius(self.center, -1.0)
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

    #_def set_control_points_by_radius(self)

    def set_control_points(self):
        """
        Test the Circle Contour set_control_pts function.
        """
        contour = self.sv_contour_object 
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
            self.logger.info("   Contour center: {0:s}".format(str(contour.Center()))) 
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong number of arguments".format(test_num))
        try:
            contour.set_control_points(1.0, 2.0)
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong argument type".format(test_num))
        try:
            contour.set_control_points(1.0)
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong type in list of control points".format(test_num))
        try:
            contour.set_control_points([ [1.0,0.0,0.0], [-1, 'b', 'c'] ])
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))

        test_num += 1
        self.logger.info("{0}. Wrong number of control points".format(test_num))
        try:
            contour.set_control_points([ [1.0,0.0,0.0] ])
        except Exception as error:
            self.logger.info("   Exception: {0}".format(error))


    #_def set_control_points(self)

#_class CircleContour(object)


class ContourTest(object):
    def __init__(self, name):
        self.name = name
        self.path_name = None
        self.path_control_points = None
        self.path = None
        self.contour = None

        self.logger_name = "contour-test" 
        self.log_file_name = "contour-test.log" 
        self.logger = self.init_logging()

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

    def create_path(self):
        self.path_name = "path1"
        self.path_control_points = []
        self.path_control_points.append([2.0, 2.0, 0.0])
        self.path_control_points.append([3.0, 3.0, 0.0])
        self.path_control_points.append([4.0, 4.0, 0.0])
        self.path_control_points.append([5.0, 5.0, 0.0])

        self.path = sv.Path.pyPath()
        self.path.NewObject(self.path_name)

        ## Set path points.
        for i in range(0,len(self.path_control_points)):
            self.path.AddPoint(self.path_control_points[i])

        ## Create path geometry.
        self.path.CreatePath()
        points = self.path.GetPathPosPts()
        control_points = self.path.GetControlPts()
        pos_pts = self.path.GetPathPosPts()
    #_def create_path(self)

    def create_circle_contour(self):
        name = "circle_contour_test"
        contour = CircleContour(name, self.logger)
        contour.radius = 1.0
        contour.path_index = 0
        contour.center = self.path_control_points[contour.path_index] 
        sv.contour.set_contour_kernel('Circle')
        contour.sv_contour_object  = sv.contour.Contour()
        contour.sv_contour_object.new_object(name, self.path_name, contour.path_index)
        return contour 
    #_def create_circle_contour(self)

    def circle_contour(self):
        self.logger.info("Testing circle contour ...")
        contour = self.create_circle_contour()

        contour.set_control_points_by_radius()

        #contour.set_control_points()

    #_def circle_contour(self)


#_class ContourTest(object)

#help(sv.contour)

## Test contour functions.
contour_test = ContourTest("contour_test")
contour_test.create_path()
contour_test.circle_contour()



