#!/bin/bash
#
# This script creates an SV .svproj file.
#
# It assumes that there is a single .vti file in the Images directory.
#
# Usage:
#
#  ./create-svproj.sh > .svproj 
#
part1="\
<?xml version='1.0' encoding='UTF-8'?>
<projectDescription version=\"1.0\">
    <images folder_name=\"Images\">
"
part3="\
    </images>
    <paths folder_name=\"Paths\"/>
    <segmentations folder_name=\"Segmentations\"/>
    <models folder_name=\"Models\"/>
    <meshes folder_name=\"Meshes\"/>
    <simulations folder_name=\"Simulations\"/>
    <simulations1d folder_name=\"Simulations1d\"/>
    <svFSI folder_name=\"svFSI\"/>
</projectDescription>
"

files=(./Images/*.vti)
file=${files[0]}
file_name=${file##*/}
name="${file_name%.*}"
part2="        <image in_project=\"yes\" path=\"${file_name}\" name=\"${name}\"/> "

echo "${part1}${part2}${part3}"


