
# Calculate centerlines for a surface model and split and group centerlines along branches.

export PATH="$HOME/vmtk/bin:$PATH"

vmtkcenterlines -ifile ${1}.vtp --pipe vmtkbranchextractor -ofile ${1}_clsp.vtp

