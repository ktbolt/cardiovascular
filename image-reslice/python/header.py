#!/usr/bin/env python
import sys
import xml.etree.ElementTree as et
import vtk
from math import sqrt
import logging
from manage import get_logger_name

class Header(object):
    def __init__(self):
        self.t00 = None
        self.t01 = None
        self.t02 = None

        self.t10 = None
        self.t11 = None
        self.t12 = None

        self.t20 = None
        self.t21 = None
        self.t22 = None

    @classmethod
    def read_header_file(cls, params):
        '''Read a header (.hdr) file. 
        '''
        logger = logging.getLogger(get_logger_name())
        file_name = params.header_file_name

        # Remove 'format' tag from xml file.
        f = open(file_name, "r")
        lines = f.readlines()

        # Create string from xml file and parse it.
        xml_string = "".join(lines)
        tree = et.ElementTree(et.fromstring(xml_string))
        root = tree.getroot()

        transform = root.find('transform_lps')
        logger.info("transform: " + str(transform.attrib))

        header = Header()
        header.t00 = float(transform.attrib['t00'])
        header.t01 = float(transform.attrib['t01'])
        header.t02 = float(transform.attrib['t02'])

        header.t10 = float(transform.attrib['t10'])
        header.t11 = float(transform.attrib['t11'])
        header.t12 = float(transform.attrib['t12'])

        header.t20 = float(transform.attrib['t20'])
        header.t21 = float(transform.attrib['t21'])
        header.t22 = float(transform.attrib['t22'])

        return header 
