
"""
This script is used to test the SV 'path' module.
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

#----------
# PathTest
#----------
#
class PathTest(object):
    """
    The PathTest class is used to test the SV path API functions.
    """
    def __init__(self, name):
        self.name = name

        self.logger_name = "path-test" 
        self.log_file_name = "path-test.log" 
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

    def path(self, visualize=False):
        """
        Test Path functions.
        """
        self.logger.info("==================================================")
        self.logger.info("                   Testing Path                   ")
        self.logger.info("==================================================")

         # Tests.
        self.create_path(visualize)
        self.replace_control_point(visualize)

    def create_path(self, name="path_test"):
        """
        Test creating a Path object.
        """
        emsg =  "   create_path: {0}"
        umsg = "  create_path: Unexpected exception: {0}"

        # Create some contol points.
        dy = 1.0
        num_path_control_pts = 5;
        path_control_points = [ [0.0, i*dy, 0.0] for i in range(0,num_path_control_pts)]
        self.logger.info("Testing create Path object")

        ## Test creating a path correctly. 
        #
        test_num = 1
        test_name = "_create_path_" 
        path_name = "path_test" + test_name + str(test_num)
        self.logger.info("{0}. Correct arguments".format(test_num))
        try:
            path = sv.path.Path()
            path.new_object(path_name)

            # Set path control points.
            for pt in path_control_points:
                path.add_control_point(pt)

            # Create path geometry.
            path.create()
            control_points = path.get_control_points()
            num_curve_points = path.get_num_curve_points()
            curve_points = path.get_curve_points()
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        ## Test creating with no control points. 
        #
        test_num += 1
        path_name = "path_test" + test_name + str(test_num)
        self.logger.info("{0}. No control points".format(test_num))
        try:
            path = sv.path.Path()
            # Create a PathElement.
            path.new_object(path_name)

            # Don't set path points.
            #for i in range(0,len(path_control_points)):
            #    path.AddPoint(path_control_points[i])

            # Create path geometry.
            path.create()
            control_points = path.get_control_points()
            points = path.get_curve_points()
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        ## Test not calling path.new_object() and add control points. 
        #
        test_num += 1
        path_name = "path_test" + test_name + str(test_num)
        self.logger.info("{0}. Don't call path.new_object()".format(test_num))
        try:
            path = sv.path.Path()
            #path.new_object(path_name)

            # Set path points.
            for i in range(0,len(path_control_points)):
                path.add_control_point(path_control_points[i])

            #points = path.get_curve_points()
            control_points = path.Get_control_points()
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        ## Test adding bad path control point. 
        #
        test_num += 1
        path_name = "path_test" + test_name + str(test_num)
        self.logger.info("{0}. Add bad control point".format(test_num))
        try:
            path = sv.path.Path()
            path.new_object(path_name)
            self.test_adding_bad_contorol_point(path, emsg, umsg)

        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

    def test_adding_bad_contorol_point(self, path, emsg, umsg):
        """
        Check various ways to set bad control points.
        """
        try:
            path.add_control_point(1.0, 2.0, 3.0)
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        try:
            path.add_control_point(1.0)
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        try:
            path.add_control_point([1.0,2])
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        try:
            path.add_control_point(['1','2','3'])
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        try:
            path.add_control_point([1.0, 2.0, 3.0])
            path.add_control_point([1.0, 2.0, 3.0])
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

    #_def check_adding_bad_contorol_point(self, path))

    def replace_control_point(self, name="path_test"):
        """
        Test creating a Path object.
        """
        emsg =  "   replace_control_point: {0}"
        umsg = "  replace_control_point: Unexpected exception: {0}"

        # Create some contol points.
        dy = 1.0
        num_path_control_pts = 5;
        path_control_points = [ [0.0, i*dy, 0.0] for i in range(0,num_path_control_pts)]
        self.logger.info("Testing create Path object")

        ## Test replacing control point correctly. 
        #
        test_num = 1
        test_name = "_replace_control_point_"
        path_name = "path_test" + test_name + str(test_num)
        self.logger.info("{0}. Correct arguments".format(test_num))

        try:
            path = sv.path.Path()
            path.new_object(path_name)
            for pt in path_control_points:
                path.add_control_point(pt)
            path.create()
            index = 1 
            pt = [1.0, 1.0, 1.0]
            path.replace_control_point(index, pt)
            control_points = path.get_control_points()
            self.logger.info("Control point at {0:d}: {1}".format(index, str(control_points[index])))
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        ## Test bad arguments. 
        #
        test_num += 1
        test_name = "_bad_args"
        path_name = "path_test" + test_name + str(test_num)
        self.logger.info("{0}. Bad arguments".format(test_num))

        try:
            path = sv.path.Path()
            path.new_object(path_name)
            for pt in path_control_points:
                path.add_control_point(pt)
            path.create()
            self.test_bad_replace_control_point(path, emsg, umsg)

        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

    #_def replace_control_point(self, name="path_test")

    def test_bad_replace_control_point(self, path, emsg, umsg):
        """
        Check various ways to replace control point.
        """
        try:
            index = 1
            pt = 1.0
            path.replace_control_point(index, pt)
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        # Reverse arguments.
        try:
            index = 1
            pt = [1.0, 1.0, 1.0]
            path.replace_control_point(pt, index)
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        # Index too large.
        try:
            index = len(path.get_control_points())
            pt = [1.0, 1.0, 1.0]
            path.replace_control_point(index, pt)
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))

        # Point wrong size.
        try:
            index = len(path.get_control_points())-2
            pt = [1.0, 1.0]
            path.replace_control_point(index, pt)
        except sv.path.PathException as error:
            self.logger.info(emsg.format(error))
        except Exception as error:
            self.logger.error(umsg.format(error))






#_class PathTest(object)

#help(sv.path)

## Test path functions.
#
path_test = PathTest("contour_test")
visualize = False
#visualize = True

# Test Path object.
path_test.path(visualize)


