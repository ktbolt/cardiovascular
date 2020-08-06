#!/usr/bin/env python

# ###########################################################
# Convert a DICOM image series into a VTK .vtk image file.
#
#   Usage:
#
#     dicom-to-vtk.py -i <DICOM_DIRECTORY> -o <VTK_DIRECTORY>
#
# ###########################################################

import argparse
import sys 
import SimpleITK as sitk


def main(data_directory, output_directory):

    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)

    if not series_IDs:
        print("ERROR: given directory \"" + data_directory + "\" does not contain a DICOM series.")
        sys.exit(1)
    print("DICOM series_IDs: " + str(series_IDs))

    # Get the series file names
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory, series_IDs[0])
    series_reader = sitk.ImageSeriesReader()
    series_reader.SetFileNames(series_file_names)
    print("Number of series file names: {0:d}".format(len(series_file_names)))

    # Configure the reader to load all of the DICOM tags (public+private)
    series_reader.MetaDataDictionaryArrayUpdateOn()
    series_reader.LoadPrivateTagsOn()
    image3D = series_reader.Execute()

    # Write the .vtk file
    basename = data_directory.split('/')[-1]
    writer = sitk.ImageFileWriter()
    writer.SetFileName(output_directory + "/" + basename + ".vtk")
    writer.Execute(image3D)


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="Convert DICOM image series into a VTK .vtk image series")

    arg_parser.add_argument(
        "-i",
        dest="data_directory",
        required=True,
        help="Top-level directory containing subdirectories of DICOM series."
    )
    arg_parser.add_argument(
        "-o",
        dest="output_directory",
        required=True,
        help="Output file directory."
    )

    args = arg_parser.parse_args()

    main(args.data_directory, args.output_directory)
