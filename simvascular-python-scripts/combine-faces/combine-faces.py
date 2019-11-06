'''
This script is used to combine two faces into a single face. 

Usage:

    simvascular --python -- combine-faces.py INFILE OUTFILE

        INFILE - .vtp mesh file.
        OUTFILE - .vtp mesh file with combinded faces.

'''
import os, pwd
import sys
import sv
import sv_vis as vis

# Set the solid modeling kernel.
sv.Solid.SetKernel('PolyData')

## Read mesh exterior .vtp file.
model_name = "model"
model_file_name = sys.argv[1] 
solid = sv.Solid.pySolidModel()
solid.ReadNative(model_name, model_file_name)

## Combine face IDs 1 and 5.
solid.CombineFaces(1, 5)

## Write the combined model. 
combined_model = sys.argv[2] 
solid.WriteNative(combined_model)

