
# Divide a surface in relation to its split and grouped centerlines.
# 
# The GroupIds cell data array groups faces into separate branches.
#
export PATH="/Users/parkerda/vmtk/bin:$PATH"

vmtkbranchclipper -ifile ${1}.vtp -centerlinesfile ${1}_clsp.vtp -ofile ${1}_sp.vtp

