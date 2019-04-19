##wgyang 2019.2
##This python script 1. extracts centerlines from a 3D model using vmtkcenterlines, 2. derives connectivity, segment length and size data from the centerline polydata and 3. generates an input file for Stanford's 1D finite element solver.
##
import math
import sys
import os
from os import path, makedirs
import pathlib
import numpy as np
import numpy.linalg as la
import vtk
from vmtk import vtkvmtk,vmtkscripts
from vtk.util import numpy_support
import vtk.util.numpy_support as nps
import os
import numpy as np
import re
############################################################################################################
## user inputs
ModelName="SU201_2005"
# use a full path if it is not under the current dir
modelpath="SU201_2005_RPA1_exterior.vtp" 
inflowfile="inflow.flow"
# provide a vtp file with wall properties if uniformat==0
wallpropmodelpath="SU201_2005_RPA1_wallprop.vtp"
meshsurfacedir=pathlib.Path('./mesh-surfaces')
inletfacename="inflow"
outletfacename=[];
outletcenters=[];
centerline_outputfile="SU201_2005_RPA1_cl.vtp"
# if centerlines were previously generated and you don't want to re-generate them, set icomputecenterlines=0 note that the previously generated path id list should be consistent with the facename list reading from mesh-surfaces
icomputecenterlines=1
#reorganize segments for a long bifurcation group
ireorgseg=0

#lcoef=1.0
#Acoef=1.0
## if the geometry is in mm, convert to cgs
lcoef=0.1
Acoef=0.01

#mesh size in a vessel segment
dx=0.1
#min number of elements for a segment
minnumfe=10
timestep=0.000588
numtimesteps=2000
tincr=20
##specify outflowBC: RCR, RESISTANCE
outflowBC="RCR"
#outflowBC="RESISTANCE"

#file for BC values 
if outflowBC=="RESISTANCE":
 BCfile="resistance.dat"
if outflowBC=="RCR":
 BCfile="rcrt.dat"

# 3Doutlet list for BCfile, the order of outlet names should be consistent with BCfile
useroutletfile="outlets.dat"
#uniform outflow BC values for all outlets, if uniformBC=0, provide a data list
uniformBC=0
#uniformmaterial property, if uniformmat=0, provide a data list
uniformmat=1

density=1.055
viscosity=0.04
mattype="OLUFSEN"
c1=0.0e7
c2=-22.5267
c3=2.65e5

#outputformat TXT or VTK
outputformat="TEXT"
###########################################################################################################


# Read a vtp file and return the polydata
def read_polydata(filename, datatype=None):
    """
    Load the given file, and return a vtkPolyData object for it.
    Args:
        filename (str): Path to input file.
        datatype (str): Additional parameter for vtkIdList objects.
    Returns:
        polyData (vtkSTL/vtkPolyData/vtkXMLStructured/
                    vtkXMLRectilinear/vtkXMLPolydata/vtkXMLUnstructured/
                    vtkXMLImage/Tecplot): Output data.
    """

    # Check if file exists
    if not path.exists(filename):
        raise RuntimeError("Could not find file: %s" % filename)

    # Check filename format
    fileType = filename.split(".")[-1]
    if fileType == '':
        raise RuntimeError('The file does not have an extension')

    # Get reader
    if fileType == 'stl':
        reader = vtk.vtkSTLReader()
        reader.MergingOn()
    elif fileType == 'vtk':
        reader = vtk.vtkPolyDataReader()
    elif fileType == 'vtp':
        reader = vtk.vtkXMLPolyDataReader()
    elif fileType == 'vts':
        reader = vtk.vtkXMinkorporereLStructuredGridReader()
    elif fileType == 'vtr':
        reader = vtk.vtkXMLRectilinearGridReader()
    elif fileType == 'vtu':
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif fileType == "vti":
        reader = vtk.vtkXMLImageDataReader()
    elif fileType == "np" and datatype == "vtkIdList":
        result = np.load(filename).astype(np.int)
        id_list = vtk.vtkIdList()
        id_list.SetNumberOfIds(result.shape[0])
        for i in range(result.shape[0]):
            id_list.SetId(i, result[i])
        return id_list
    else:
        raise RuntimeError('Unknown file type %s' % fileType)

    # Read
    reader.SetFileName(filename)
    reader.Update()
    polydata = reader.GetOutput()

    return polydata

def write_polydata(input_data, filename, datatype=None):
    """
    Write the given input data based on the file name extension.
    Args:
        input_data (vtkSTL/vtkPolyData/vtkXMLStructured/
                    vtkXMLRectilinear/vtkXMLPolydata/vtkXMLUnstructured/
                    vtkXMLImage/Tecplot): Input data.
        filename (str): Save path location.
        datatype (str): Additional parameter for vtkIdList objects.
    """
    # Check filename format
    fileType = filename.split(".")[-1]
    if fileType == '':
        raise RuntimeError('The file does not have an extension')

    # Get writer
    if fileType == 'stl':
        writer = vtk.vtkSTLWriter()
    elif fileType == 'vtk':
        writer = vtk.vtkPolyDataWriter()
    elif fileType == 'vts':
        writer = vtk.vtkXMLStructuredGridWriter()
    elif fileType == 'vtr':
        writer = vtk.vtkXMLRectilinearGridWriter()
    elif fileType == 'vtp':
        writer = vtk.vtkXMLPolyDataWriter()
    elif fileType == 'vtu':
        writer = vtk.vtkXMLUnstructuredGridWriter()
    elif fileType == "vti":
        writer = vtk.vtkXMLImageDataWriter()
    elif fileType == "np" and datatype == "vtkIdList":
        output_data = np.zeros(input_data.GetNumberOfIds())
        for i in range(input_data.GetNumberOfIds()):
            output_data[i] = input_data.GetId(i)
        output_data.dump(filename)
        return
    else:
        raise RuntimeError('Unknown file type %s' % fileType)

    # Set filename and input
    writer.SetFileName(filename)
    writer.SetInputData(input_data)
    writer.Update()

    # Write
    writer.Write()


# Calculate the centroid of a vtp file
def centroid(infile):
    poly_data = read_polydata(infile)
    x_list = []
    y_list = []
    z_list = []
    for i in range(poly_data.GetNumberOfPoints()):
        x_list.append(float(poly_data.GetPoints().GetPoint(i)[0]))
        y_list.append(float(poly_data.GetPoints().GetPoint(i)[1]))
        z_list.append(float(poly_data.GetPoints().GetPoint(i)[2]))

    return [np.mean(x_list), np.mean(y_list), np.mean(z_list)]

#Step 1. Extract centerlines
#Step 1 can be done from a terminal command line #vmtkcenterlines -ifile wall_combined.vtp --pipe vmtkcenterlineattributes --pipe vmtkbranchextractor -seedselector profileidlist -sourceids 0 -ofile SU201_2005_cl.vtp  
# use a wall only vtp file (no caps), id 0 usually is the inlet. and paths will be generated from the inlet to all outlets 

#1.1 identify inlet and outlet facenames and centers from mesh-surfaces
for facefile in meshsurfacedir.iterdir():
 
  filename = facefile.name
  if not filename.lower().startswith('wall'):
    if facefile.stem=="inflow" and (facefile.suffix ==".vtk" or facefile.suffix ==".vtp"):
      inletpath=str(facefile.absolute())
      print( "inlet= ",filename)
      polydata=read_polydata(inletpath)
      inletcenter=centroid(inletpath)
    #  print "inletcenters: ",inletcenter
    if facefile.stem!="inflow" and (facefile.suffix ==".vtk" or facefile.suffix ==".vtp"):
      outletpath=str(facefile.absolute())
      outletfacename.append(facefile.stem)
      print( "outlet=",filename)
      outletcenters.extend(centroid(outletpath))
 
print ("Number of outletfacenames=",len(outletfacename))
#1.2 read BC files if uniformBC!=1
if uniformBC==0:
  print("####### outletfacename: ", outletfacename)
  BClist=[]
  with open(BCfile) as file:
   if outflowBC=="RESISTANCE":
     for line in file:
      print ("line=",line)
      BClist.append(float(line))
     if len(BClist)!=len(outletfacename):
      print( "The number of BC values =",len(BClist)," is not consistant with the number of outlets=",len(outletfacename),"exit.")
      exit()
   if outflowBC=="RCR":
      keyword = file.readline()
     # print"keyword=",keyword
      while True:
        tmp=file.readline()
        if tmp==keyword:
         RCRval=[]
         RCRval.append(float(file.readline()))
         RCRval.append(float(file.readline()))
         RCRval.append(float(file.readline()))
         BClist.append(RCRval)
        if len(tmp)==0:
       #   print "eof"
          break

  useroutletname=[]
  with open(useroutletfile) as file:
   for line in file:
     useroutletname.extend(line.splitlines())
  print( "Number of user provided model outlet names=",len(useroutletname)  )
  if len(useroutletname)!=len(outletfacename):
      print( "The number of user provided outlets is not consistant with the number of outlets in mesh-surfaces. Exit.")
      exit()

#1.4 call vmtkcenterlines by providing source points and endpoints
model=read_polydata(modelpath)
if icomputecenterlines==1:
  centerlines = vmtkscripts.vmtkCenterlines()
  centerlines.Surface=model
  centerlines.SeedSelectorName = "pointlist"
  centerlines.AppendEndPoints = 1
  centerlines.SourcePoints = inletcenter
  centerlines.TargetPoints = outletcenters
  centerlines.Execute()
  centerlines_output = centerlines.Centerlines
  centerlines_output = centerlines.Centerlines


  branchextractor=vmtkscripts.vmtkBranchExtractor()
  branchextractor.Centerlines=centerlines_output
  branchextractor.Execute()
  centerlines_output=branchextractor.Centerlines
  write_polydata(centerlines_output,centerline_outputfile)


#step 2 Obtain connectivity, seg length/size information

#FileName="SU201_2005_RPA1_cl.vtp"
#ModelName="SU201_2005_RPA1"
#FileName="SU201_2005_LPA_cl.vtp"
#ModelName="SU201_2005_LPA"

#FileName="SU201_2005_cl.vtp"
#ModelName="SU201_2005"


#print FileName
#datareader=vtk.vtkXMLPolyDataReader()
#datareader.SetFileName(FileName)
#datareader.Update()

#model=vtk.vtkPolyData()
#model=datareader.GetOutput()
#num_pts=model.GetNumberOfPoints()

#2.1 read centerline polydata
model=read_polydata(centerline_outputfile)
num_pts=model.GetNumberOfPoints()
print ("Number of Points:", model.GetNumberOfPoints())

print ("Number of arrays:", model.GetCellData().GetNumberOfArrays())

#a cell/element (named as LINE) is a segment/line that consists of n points.
# A centerline consists of m cells, m=number of tract ids, the length of a cell/line is an approximation of a group. 
# In Cell Data, lines are listed from 0 to m. For each line, the first number is the number of points for this line followed by 1st point to the last point.
num_cells=model.GetNumberOfCells()
print ("Number of Cells:", model.GetNumberOfCells())

###read cell data, for each cell (line), the lists record its centerline id (n lines starting from the inlet to outlets), blanking (0 non bifurcation, 1 bifurcation), 
###group ids (vessels are splitted into single segments/branches and a bifurcation region, 
###if a vessel shared by multiple centerlines, there multiple elements sharing the same group id
###if a segment is the terminal segment without any child elements, its group id is unique.
###for a bifurcation region, the elemens' blanking is 1.

celldata=model.GetCellData().GetArray("CenterlineIds")
centerline_list = nps.vtk_to_numpy(celldata)

celldata=model.GetCellData().GetArray("Blanking")
blank_list = nps.vtk_to_numpy(celldata)

celldata=model.GetCellData().GetArray("GroupIds")
group_list = nps.vtk_to_numpy(celldata)

celldata=model.GetCellData().GetArray("TractIds")
tract_list = nps.vtk_to_numpy(celldata)




num_path=centerline_list[-1]+1
print ("number of paths=", num_path)

num_group=max(group_list)+1
print ("number of groups=",num_group)


###path_elems[i] records the element(line) indices for centerline id=i
path_elems=[]

for i in range(0,num_path):
 path_elems.append([])

for i in range(0,num_path):
  for j in range(0,num_cells):
    if i==centerline_list[j]: 
     path_elems[i].append(j)

#for i in range(0,num_path):
# print "centerline",i,"groups ids",path_elems[i]

###group_elems[i] records the element(line) indices for group id=i
group_elems=[]
for i in range(0,num_group):
  group_elems.append([])


for i in range(0,num_cells):
#  print "cellid=",i
#  print "groupid=",group_list[i]
  group_elems[group_list[i]].append(i)

#for i in range(0,num_group):
# print "group",i, "element ids", group_elems[i]

## handling variable outflow BCs
## create a mapping from the pathlist (outletfacename) to user-provided 3D outletlist (outlets.dat)
if uniformBC==0:
 path2useroutlet=[]
 for i in range(0,num_path):
  for j in range(0,len(useroutletname)):
     if outletfacename[i]==useroutletname[j]:
       path2useroutlet.append(j)
       break

 print("####### outletfacename: ", outletfacename)
 print("####### useroutletname: ", useroutletname)
 print("####### path2useroutlet: ", path2useroutlet)

# print "path to user outlet=",path2useroutlet

if uniformmat==0:
 matlist=[]
 poly_data=read_polydata(wallpropmodelpath)
 #point_data = polydata.GetPointData()
 #wallprop = nps.vtk_to_numpy(point_data.GetArray('wallproperty'))
 
 branchclip=vmtkscripts.vmtkBranchClipper()
 branchclip.Surface=poly_data
 branchclip.Centerlines=centerlines_output
 branchclip.Execute()
 branchclip_output=branchclip.Surface
 branchclip_outputfile="wall_prop_grouped.vtp"
 write_polydata(branchclip_output,branchclip_outputfile)
 point_data=branchclip_output.GetPointData()
 #wallprop=nps.vtk_to_numpy(point_data.GetArray('wallproperty'))
 thickness=nps.vtk_to_numpy(point_data.GetArray('thickness'))
 E=nps.vtk_to_numpy(point_data.GetArray('Young_Mod'))
 nodegroup=nps.vtk_to_numpy(point_data.GetArray('GroupIds'))

 
 group_thickness=[]
 group_E=[]

 for i in range(0,num_group):
  group_thickness.append([])
  group_E.append([])

 for i in range(0,poly_data.GetNumberOfPoints()):
     group_thickness[nodegroup[i]].append(float(thickness[i]))
     group_E[nodegroup[i]].append(float(E[i]))
     
 for i in range(0,num_group):
  matlist.append([np.mean(group_thickness[i]), np.mean(group_E[i])])
 





#2.2 calculate connectivity
###group_terminal, 0: it is not a terminal group 2:it is a bifurcation, 1: it is a terminal group/outlet

group_terminal=[0]*num_group
num_outlet=0
num_bif=0
tmp=len(group_elems[0])
for i in range(0,num_group):
 if blank_list[group_elems[i][0]]==1:
  group_terminal[i]=2
  num_bif=num_bif+1
 if len(group_elems[i])==1 and blank_list[group_elems[i][0]]!=1:
  group_terminal[i]=1
  num_outlet=num_outlet+1
  
 if len(group_elems[i])>tmp and blank_list[group_elems[i][0]]!=1:
  tmp=len(group_elems[i])
  print("A group with id>0 contains more centerlines than group 0" )




if tmp!=len(group_elems[0]) or tmp!=num_outlet or num_path!=num_outlet:
 print ("warning: inlet group id is not 0 or number of centerlines is not equal to the number of outlets")
 print ("num_path=",num_path,"num_outlet=",num_outlet,"len(group_elems[0])=",len(group_elems[0]),"tmp=",tmp)
 exit()
# non-bifurcation groups are trated as segments in the 1D solver
num_seg=num_group-num_bif
### bifurcation groups are condensed into bifurcation nodes using the centroid, 
### inlet and outlet are created by using the first and last points in the group respectively
num_node=num_bif+num_outlet+1

### seg_list[i] records the group id for seg i

seg_list=[]
group_seg=[]

print ("group_terminal=",group_terminal)


for i in range(0,num_group):
 if group_terminal[i]!=2:
   seg_list.append(i)
   group_seg.append(len(seg_list)-1)
 else:
   group_seg.append(-1)

print ("seg_list=",seg_list)
print ("group_seg=",group_seg)
print ("group_elems=",group_elems)
print ("group_list=",group_list)

if len(seg_list)!=num_seg:
 print ("Error! length of seg_list is not equal to num_seg")
 exit()

### create connectivity for segments
connectivity=[]

print ("centerline_list=",centerline_list)

for i in range(0,num_seg):
     print ("----- i ",i)
  ##if  groupid is not a terminal seg, then it is a parent seg
     if group_terminal[seg_list[i]]==0:
       pargroupid=seg_list[i]
       temp_conn=[]
       temp_conn.append(pargroupid)
       print ("parent group id=",pargroupid)
  ## for each non-terminal group, at least there are 2 paths going through the child segments and sharing this group   
       pathid1=centerline_list[group_elems[pargroupid][0]]
       tractid1=tract_list[group_elems[pargroupid][0]]
  ## find the corresponding element id in path_elems list and index+1 is the bifurcation index+2 is the child elem
       childelemid1=path_elems[pathid1][tractid1+2]
       childgroupid1=group_list[childelemid1]
       temp_conn.append(childgroupid1)     
  ## find second child or third/fourth child
       for j in range(len(group_elems[pargroupid])-1,0,-1):
         temppathid=centerline_list[group_elems[pargroupid][j]]
         temptractid=tract_list[group_elems[pargroupid][j]]
         tempelemid= path_elems[temppathid][temptractid+2]
         tempgroupid=group_list[tempelemid]
         repeat=0
         for k in range (1,len(temp_conn)):
            if tempgroupid == temp_conn[k]:
              repeat=1 
              break
         if repeat==0:
          temp_conn.append(tempgroupid)
       if len(temp_conn)>3:
         print ("there are more than 2 child segments for groupid=",pargroupid)
       connectivity.append(temp_conn)

print ("connectivity in terms of groups",connectivity    )

seg_connectivity=[]
for i in range(0, len(connectivity)):
  temp_conn=[]
  for j in range(0,len(connectivity[i])):
    temp_conn.append(group_seg[connectivity[i][j]])
   
  seg_connectivity.append(temp_conn)


print ("connectivity in terms of segments",seg_connectivity )

#output some axuiliary files
file = open("connectivity_groupid.dat", "w")
for i in range(0,len(connectivity)):
 for j in range(0, len(connectivity[i])):
   file.write(str(connectivity[i][j])+" ")
 file.write("\n")
file.close()


if len(outletfacename)!=0: 
 #output outlet face names with the corresponding group id
 file = open("outletface_groupid.dat", "w")
 for i in range(0,num_group):
    if group_terminal[i]==1:
        tempelemid=group_elems[i][0]
        temppathid=centerline_list[tempelemid]
        file.write(outletfacename[temppathid]+" "+"GroupId "+str(i)+"\n")
 file.close()

file = open("centerline_groupid.dat", "w")
for i in range(0,num_path):
    file.write("Centerline "+str(i)+" "+str(group_list[path_elems[i][0]]))
    tmpgroupid=group_list[path_elems[i][0]]
    for j in range(1,len(path_elems[i])):
      if group_list[path_elems[i][j]]!=tmpgroupid:
        file.write(" "+str(group_list[path_elems[i][j]]))
        tmpgroupid=group_list[path_elems[i][j]]
    file.write("\n")

file.close()

#2.3 calculate seg length, Ain and Aout

group_length=[]
group_Ain=[]
group_Aout=[]
seg_head=[]
seg_rear=[]
celldata=model.GetPointData().GetArray("MaximumInscribedSphereRadius")
points_maxR=nps.vtk_to_numpy(celldata)

for i in range(0,num_group):
  
   tmpl=0.0
   tmpAin=0.0
   tmpAout=0.0
   for j in range(0,len(group_elems[i])):
     ids=vtk.vtkIdList()
     model.GetCellPoints(group_elems[i][j],ids)
     num_ids=ids.GetNumberOfIds()
     tmpAin=tmpAin+points_maxR[ids.GetId(0)]**2*3.14
     tmpAout=tmpAout+points_maxR[ids.GetId(num_ids-1)]**2*3.14
     for k in range(0,num_ids-2):
      id1=ids.GetId(k)
      id2=ids.GetId(k+1)
      pt1=np.array([model.GetPoints().GetPoint(id1)[0],model.GetPoints().GetPoint(id1)[1],model.GetPoints().GetPoint(id1)[2]])
      pt2=np.array([model.GetPoints().GetPoint(id2)[0],model.GetPoints().GetPoint(id2)[1],model.GetPoints().GetPoint(id2)[2]])
      tmpl=tmpl+np.linalg.norm(pt2-pt1)

  #  tmp=tmp+sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2+(pt1[2]-pt2[2])**2)
   tmpl=tmpl/len(group_elems[i])*lcoef
   tmpAin=tmpAin/len(group_elems[i])*Acoef
   tmpAout=tmpAout/len(group_elems[i])*Acoef
   if tmpAin<tmpAout and group_terminal[i] !=2 :
     print("warning! Ain<Aout in group id=",i)
     print("set Ain=Aout")
     tmpAin=tmpAout
  # for bifurcation group, approximate as a straight uniform cylinder
   if group_terminal[i] ==2 :
     tmpAin=(tmpAin+tmpAout)/2.0
     tmpAout=tmpAin
   print( "group id=",i,"averaged length=", tmpl,"averaged Ain and Aout",tmpAin,tmpAout)
   group_length.append(tmpl)
   group_Ain.append(tmpAin)
   group_Aout.append(tmpAout)


# modify seg length, add bifurcation group length to the parent group
for i in range(0,num_seg):
   if group_terminal[seg_list[i]]!=1:
    pargroupid=seg_list[i]
    pathid1=centerline_list[group_elems[pargroupid][0]]
    tractid1=tract_list[group_elems[pargroupid][0]]
    #find the bifurcation group
    bifelem=path_elems[pathid1][tractid1+1]
    bifgroupid=group_list[bifelem]
    #add the bifurcation group length to the parent group
    print( "biflength ",group_length[bifgroupid],"ratio to parent group length",group_length[bifgroupid]/group_length[pargroupid])
    group_length[pargroupid]=group_length[pargroupid]+group_length[bifgroupid]
   
#2.4 get node coordinates
nodes=[]
## parent gourp id for node(i)
grouprearnodeid=[]
ids=vtk.vtkIdList()
model.GetCellPoints(0,ids)
id1=ids.GetId(0)
nodes.append(model.GetPoints().GetPoint(id1))

for i in range(0,num_group):
  if group_terminal[i]==0 or group_terminal[i]==1:
     tempelemid=group_elems[i][0]
     model.GetCellPoints(tempelemid,ids)
     num_ids=ids.GetNumberOfIds()
     id1=ids.GetId(num_ids-1)
     nodes.append(model.GetPoints().GetPoint(id1))
     grouprearnodeid.append(len(nodes)-1)
  else:
     # bifurcation group doesn't get a node id, use nodeid=-1 
     grouprearnodeid.append(-1)
print ("number of nodes= ",len(nodes))
print ("group rear node id", grouprearnodeid     )

for i in range(0,num_seg):
  tempgroupid=seg_list[i]
  if tempgroupid==0:
    seg_head.append(0)
  else:
    tempelemid=group_elems[tempgroupid][0]
    temptractid=tract_list[tempelemid]
    temppathid=centerline_list[tempelemid]
    tempelemid=path_elems[temppathid][temptractid-2]
    seg_head.append(grouprearnodeid[group_list[tempelemid]])
 
  seg_rear.append(grouprearnodeid[tempgroupid])

print( "seg_head", seg_head)
print( "seg_rear", seg_rear)

#2.5 reorgazie child segments when ireorgseg==1 and the number of child segments>3
print ("num_seg= line601",len(seg_list))
if ireorgseg==1:
 i=0
 while i < len(seg_connectivity):
   if len(seg_connectivity[i])>4:
      print ("reorganize seg connectivity=",seg_connectivity[i])
      parsegid=seg_connectivity[i][0]
      pargroupid=seg_list[parsegid]
      num_child=len(seg_connectivity[i])-1
      pathid1=centerline_list[group_elems[pargroupid][0]]
      tractid1=tract_list[group_elems[pargroupid][0]]
      #find the bifurcation group
      bifelem=path_elems[pathid1][tractid1+1]
      bifgroupid=group_list[bifelem]
      bifl=group_length[bifgroupid]
      dl=bifl/(num_child-2)
      childsegs=[]
      childsegs.extend(seg_connectivity[i][1:])
      #prevously add bif group length to the par group length
      group_length[pargroupid]=group_length[pargroupid]-bifl
      
      ids=vtk.vtkIdList()
      model.GetCellPoints(group_elems[pargroupid][0],ids)
      num_ids=ids.GetNumberOfIds()
      id1=ids.GetId(num_ids-1) #last node for par seg
      pt1=np.array([model.GetPoints().GetPoint(id1)[0],model.GetPoints().GetPoint(id1)[1],model.GetPoints().GetPoint(id1)[2]])
      childseg_dist=[]
      # sort child segments based on the distance to the parent segment, and add extra segments along the bifurcation segments instead of connecting all n child segments to 1 outlet
      for j in range(0, len(childsegs)):
        childgroupid1=seg_list[childsegs[j]]
        ids=vtk.vtkIdList()
        model.GetCellPoints(group_elems[childgroupid1][0],ids)
        id2=ids.GetId(0) # first node in each child seg
        pt2=np.array([model.GetPoints().GetPoint(id2)[0],model.GetPoints().GetPoint(id2)[1],model.GetPoints().GetPoint(id2)[2]])
        childseg_dist.append(np.linalg.norm(pt2-pt1))
      print ("childsegs=",childsegs)
      print ("dist=",childseg_dist)
      dist_order=np.argsort(childseg_dist)
      print ("order=",dist_order)
      # define bif group starting point and tangential vector
      ids=vtk.vtkIdList()
      model.GetCellPoints(group_elems[bifgroupid][0],ids)
      num_ids=ids.GetNumberOfIds()
      id1=ids.GetId(0) 
      pt1=np.array([model.GetPoints().GetPoint(id1)[0],model.GetPoints().GetPoint(id1)[1],model.GetPoints().GetPoint(id1)[2]])
      id2=ids.GetId(int(num_ids/2)) 
      pt2=np.array([model.GetPoints().GetPoint(id2)[0],model.GetPoints().GetPoint(id2)[1],model.GetPoints().GetPoint(id2)[2]])
      v=pt2-pt1
      v=v/np.linalg.norm(v)
     
      first_new_seg=len(seg_list)
      parrearnodeid=seg_rear[parsegid]
      if len(seg_list)!=len(seg_head) or len(seg_list)!=len(seg_rear):
        print ("Something wrong! length of seg_list != length seg_head/seg_rear")
      # split the bif group into n-2 pieces and change the corresponding group length 
      for j in range(0,num_child-2):
        seg_list.append(bifgroupid)
      # add rear node for each new seg
        pt2=pt1+v*dl
        nodes.append([pt2[0],pt2[1],pt2[2]])
        seg_rear.append(len(nodes)-1)
        seg_head.append(parrearnodeid)
        pt1=pt2
        parrearnodeid=len(nodes)-1

      # modify the group length. the group is splitted into n-2 segments, the length represents the segment length now.
      group_length[bifgroupid]=group_length[bifgroupid]/(num_child-2)

      #delete original connectivity with >3 child segments, add new segments splitted from the bif group to the connectivity and connect to child segments
      del seg_connectivity[i]
      i=i-1
      temp_conn=np.zeros((1+num_child-2,3)).astype(int)
      temp_conn[0][0]=parsegid
      #add splitted segments to the parement seg position 
      for j in range(0,num_child-2):   
        temp_conn[j+1][0]=first_new_seg+j
      # add child segment ids to the temp_conn
      for j in range(0,num_child-2):
        temp_conn[j][1]=first_new_seg+j
        temp_conn[j][2]=childsegs[dist_order[j]]
      # add last two child segments to temp_conn      
      temp_conn[num_child-2][1]=childsegs[dist_order[num_child-2]]
      temp_conn[num_child-2][2]=childsegs[dist_order[num_child-1]]
      for j in range(0,num_child-1):
        seg_connectivity.append(temp_conn[j])

      #modify head nodes for child segments
      for j in range(0, num_child-2):
        sorted_child_index=dist_order[j]
        seg_head[childsegs[sorted_child_index]]=seg_head[first_new_seg+j]
     
      seg_head[childsegs[dist_order[num_child-2]]]=seg_rear[-1]
      seg_head[childsegs[dist_order[num_child-1]]]=seg_rear[-1]

   i=i+1
print ("num_seg=",num_seg)
num_seg=len(seg_list)   
print ("redefine num_seg=",num_seg)
#Step 3 output a 1D input file
#
# Open file
file = open(ModelName + ".in", "w")

# Write header
file.write("# ================================\n# " + ModelName + " MODEL - UNITS IN CGS\n# ================================\n\n")
  



# Model Header
file.write("# ==========\n# MODEL CARD\n# ==========\n# - Name of the model (string)\n\n")
file.write("MODEL " + ModelName + " \n\n")
# Node Header
file.write("\n\n### DO NOT CHANGE THIS SECTION - generated automatically \n#")
file.write("\n# ==========\n# NODE CARD\n# ==========\n# - Node Name (double)\n# - Node X Coordinate (double)\n# - Node Y Coordinate (double)\n# - Node Z Coordinate (double)\n\n")


for i in range(0,len(nodes)):
  file.write("NODE " + str(i) + " " + str(nodes[i][0]*lcoef) + " " + str(nodes[i][1]*lcoef) + " " + str(nodes[i][2]*lcoef) + "\n")
 


# Joint Header
file.write("\n\n\n### DO NOT CHANGE THIS SECTION - generated automatically \n#")
file.write("\n# ==========\n# JOINT CARD\n# ==========\n# - Joint Name (string)\n# - Joint Node (double)\n# - Joint Inlet Name (string)\n# - Joint Outlet Name (string)\n\n")

# JointInlet and JointOutlet Header
file.write("\n### DO NOT CHANGE THIS SECTION - generated automatically \n#")
file.write("\n# ================================\n# JOINTINLET AND JOINTOUTLET CARDS\n# ================================\n# - Inlet/Outlet Name (string)\n# - Total Number of segments (int)\n# - List of segments (list of int)\n\n")            

 
for i in range(0,len(seg_connectivity)):
  pargroupid=seg_connectivity[i][0]
  file.write("JOINT J" + str(i) + " " + str(seg_rear[pargroupid]) + " IN" + str(i) + " OUT" + str(i) + "\n")

  file.write("JOINTINLET IN" + str(i) + " " + "1 " + str(seg_connectivity[i][0]) + "\n")
  file.write("JOINTOUTLET OUT" + str(i) + " " + str(len(seg_connectivity[i])-1))
  for j in range(1,len(seg_connectivity[i])): 
     file.write(" " + str(seg_connectivity[i][j]))
  file.write("\n\n")
  # Segment Header
file.write("# ============\n# SEGMENT CARD\n# ============\n# - Segment Name (string)\n# - Segment ID (int)\n# - Segment Length (double)\n# - Total Finite Elements in Segment (int)\n# - Segment Inlet Node (int)\n# - Segment Outlet Node (int)\n# - Segment Inlet Area (double)\n# - Segment Outlet Area (double)\n# - Segment Inflow Value (double)\n# - Segment Material (string)\n# - Type of Loss (string - 'NONE','STENOSIS','BRANCH_THROUGH_DIVIDING','BRANCH_SIDE_DIVIDING','BRANCH_THROUGH_CONVERGING',\n#                          'BRANCH_SIDE_CONVERGING','BIFURCATION_BRANCH')\n# - Branch Angle (double)\n# - Upstream Segment ID (int)\n# - Branch Segment ID (int)\n# - Boundary Condition Type (string - 'NOBOUND','PRESSURE','AREA','FLOW','RESISTANCE','RESISTANCE_TIME','PRESSURE_WAVE',\n#                                     'WAVE','RCR','CORONARY','IMPEDANCE','PULMONARY')\n# - Data Table Name (string)\n\n")  

for i in range(0,num_seg):
   if uniformmat==1:
     matname="MAT1"
   else:
     matname="MAT_group"+str(seg_list[i])
   
   numfe=int(round(group_length[seg_list[i]]/dx))
   if numfe<minnumfe:
     numfe=minnumfe

   file.write("SEGMENT" + " " + 
     "Group"+ str(seg_list[i])+"_Seg"+str(i) + " " + str(i) + " "+ 
     str(group_length[seg_list[i]]) + " " + str(numfe) + " "+ 
     str(seg_head[i]) + " " + str(seg_rear[i]) + " " + 
     str(group_Ain[seg_list[i]])+ " " + 
     str(group_Aout[seg_list[i]])+ " " +"0.0 "+ 
     matname + " NONE 0.0 0 0 ")

   if group_terminal[seg_list[i]]==1:
      if uniformBC==1:
        file.write(outflowBC+ " " + outflowBC +"_1 \n")
      else:
        tempgroupid=seg_list[i]
        tempelemid=group_elems[tempgroupid][0]
        temppathid=centerline_list[tempelemid]
        print("######## add segment: ", i)
        print("    temppathid: ", temppathid)
        print("    path2useroutlet[temppathid]: ", path2useroutlet[temppathid])
        file.write(outflowBC+ " "+ outflowBC +"_"+str(path2useroutlet[temppathid])+ " \n")
   else:
      file.write("NOBOUND NONE \n")   


file.write("\n\n")
if uniformBC==1:
   file.write("DATATABLE " + outflowBC +"_1 LIST \n")
   file.write(" \n")
   file.write("ENDDATATABLE \n \n")
else:
   if outflowBC=="RCR":
    for i in range(0,num_path):
     file.write("DATATABLE " + outflowBC +"_"+str(i)+" LIST \n")
     for j in range(0, len(BClist[i])):
      file.write("0.0 "+ str(BClist[i][j]) +" \n")
     file.write("ENDDATATABLE \n \n")
   if outflowBC=="RESISTANCE":
    for i in range(0,num_path):
     file.write("DATATABLE " + outflowBC +"_"+str(i)+" LIST \n")
     file.write("0.0 "+ str(BClist[i]) +" \n")
     file.write("ENDDATATABLE \n \n")   

file.write("\n\n")
file.write("DATATABLE INFLOW LIST \n")
if len(inflowfile)==0:
 file.write("Copy and paste inflow data here. \n")
else:
   with open(inflowfile) as inflow:
     for line in inflow:
       file.write(line)
file.write("ENDDATATABLE \n")  
file.write("\n\n")

# SolverOptions Header
file.write("# ==================\n# SOLVEROPTIONS CARD\n# ==================\n# - Solver Time Step (double), \n# - Steps Between Saves (int), \n# - Max Number of Steps (int)\n# - Number of quadrature points for finite elements (int), \n# - Name of Datatable for inlet conditions (string)\n# - Type of boundary condition (string - 'NOBOUND','PRESSURE','AREA','FLOW','RESISTANCE','RESISTANCE_TIME','PRESSURE_WAVE',\n#                                        'WAVE','RCR','CORONARY','IMPEDANCE','PULMONARY')\n# - Convergence tolerance (double), \n# - Formulation Type (int - 0 Advective, 1 Conservative), \n# - Stabilization (int - 0 No stabilization, 1 With stabilization)\n\n")
file.write("SOLVEROPTIONS "+ str(timestep)+ " "+ str(tincr) +" "+ str(numtimesteps) + " 2 INFLOW FLOW 1.0e-5 1 1\n\n")



  # Material Header
file.write("# =============\n# MATERIAL CARD\n# =============\n# - Material Name (string)\n# - Material Type (string - 'LINEAR','OLUFSEN')\n# - Material Density (double)\n# - Material Viscosity (double)\n# - Material Exponent (double)\n# - Material Parameter 1 (double)\n# - Material Parameter 2 (double)\n# - Material Parameter 3 (double)\n\n")

if uniformmat==1:
   file.write("MATERIAL MAT1 " + mattype+" " + str(density)+" "+str(viscosity)+" " + "0.0 1.0 "+str(c1)+" "+str(c2)+" "+str(c3)+ " \n")

if uniformmat==0:
   for i in range(0,num_seg):
     tmp=4.0/3.0*matlist[seg_list[i]][0]*matlist[seg_list[i]][1]/math.sqrt((group_Ain[seg_list[i]]+group_Aout[seg_list[i]])/2/3.14)
     file.write("MATERIAL MAT_group"+str(seg_list[i])+ " " + mattype+" " + str(density)+" "+str(viscosity)+" " + "0.0 1.0 "+str(c1)+" "+str(c2)+" "+str(tmp)+ " \n") 


# Output Header
file.write("\n# ============\n# OUTPUT CARD\n# ============\n#\n# 1. Output file format. The following output types are supported:\n#\t\tTEXT. The output of every segment is written in separate text files for the flow rate, pressure, area and Reynolds number. The rows contain output values at varying locations along the segment while columns contains results at various time instants.\n#\t\tVTK. The results for all time steps are plotted to a 3D-like model using the XML VTK file format.\n# 2. VTK export option. Two options are available for VTK file outputs:\n#\t\t0 - Multiple files (default). A separate file is written for each saved increment. A pvd file is also provided which contains the time information of the sequence. This is the best option to create animations.\n#\t\t1 - The results for all time steps are plotted to a single XML VTK file.\n\n")  
# Output properties
file.write("OUTPUT "+outputformat)
file.write("\n") 

# Close file
file.close()
