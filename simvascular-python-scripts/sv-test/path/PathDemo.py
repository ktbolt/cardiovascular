#import modules
from sv import *

#Create new path object
p = Path.pyPath()
p.NewObject('path1')

#Control point operations
p.AddPoint([518.0, 11.0, 165.0])
p.AddPoint([519.0, 10.0, 162.0])
p.AddPoint([521.0, 8.0, 160.0])
p.AddPoint([520.0, 9.0, 162.0], 2) 
p.AddPoint([382.0, 103.0, 198.0], 0) 

p.PrintPoints()

#Generate path points
p.CreatePath()


