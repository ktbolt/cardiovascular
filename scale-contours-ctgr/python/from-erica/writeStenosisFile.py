import sys
import numpy as np
from numpy import genfromtxt
import pdb
import numpy as np
import scipy as sp
from scipy.spatial import ConvexHull
import re

def writeStenosisFile(filename, contourGroup, st):
    inFile = open(filename+'.ctgr', 'r')
    outFile = open(filename+str(int(round((1-st)*100)))+'.ctgr','w+')
    data = []
    print("Creating "+filename+str(int(round((1-st)*100)))+'.ctgr'+"...")
    for line in inFile:
       if '<contour id=\"'+str(contourGroup)+'\"' in line:
           outFile.write(line)
           break
       else:
           outFile.write(line)

    for line in inFile:
       if '<control_points>' in line:
           break
       else:
           outFile.write(line)

    for line in inFile:
       if '</control_points>' in line:
           break
       else:
           data.append(re.findall('"([^"]*)"', line))

    ct = int(data[-1][0])

    for line in inFile:
       if '<contour_points>' in line:
           break

    for line in inFile:
       if '</contour_points>' in line:
           break
       else:
           data.append(re.findall('"([^"]*)"', line))

    data = np.array(data)[:,1:]
    P = data.astype(np.float)

    A = np.array([P[0,0],P[0,1],P[0,2]])
    B = np.array([P[1,0],P[1,1],P[1,2]])
    C = np.array([P[2,0],P[2,1],P[2,2]])

    AB = A-B
    AC = A-C

    N = np.cross(AB,AC)

    U = AB/np.linalg.norm(AB)
    uN = N/np.linalg.norm(N)

    V = np.cross(U, uN)

    u = A+U
    v = A+V
    n = A+uN


    D = np.array([[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,1,1,1]])
    S = np.array([[A[0],u[0],v[0],n[0]],[A[1],u[1],v[1],n[1]],[A[2],u[2],v[2],n[2]],[1,1,1,1]])

    M = np.matmul(D, np.linalg.inv(S))

    P = np.transpose(P)
    O = np.ones((1, P.shape[1]))
    Z = np.zeros((1, P.shape[1]))
    P = np.vstack((P,O))

    P_new = np.matmul(M, P)
    points = np.transpose(P_new[:2, :])
    hull = ConvexHull(points)
    A_orig = hull.volume

    numPts = 1000
    x = np.linspace(1, 0.001, num=numPts)
    points_old = points
    A_old = A_orig
    x_old = 1
    A_target = A_orig*st
    for i in range(numPts):
        points_new = points*x[i]
        hull_new = ConvexHull(points_new)
        x_new = x[i]
        A_new = hull_new.volume
        if abs(A_new - A_target) < abs(A_old - A_target):
            A_old = A_new
            points_old = points_new
            x_old = x_new

    Pst = np.transpose(points_old)

    Pst = np.vstack((Pst,Z,O))
    P_final = np.matmul(np.linalg.inv(M), Pst)
    P_out = np.transpose(P_final)[:,0:3]

    outFile.write('            <control_points>\n')
    for i in range(ct+1):
        dl = P_out[i,:]
        fStr = '<point id=\"{}\" x=\"{}\" y=\"{}\" z=\"{}\" />\n'.format(i,dl[0],dl[1],dl[2])
        outFile.write('                '+fStr)
    outFile.write('            </control_points>\n')

    outFile.write('            <contour_points>\n')
    for i in range(ct+1, np.shape(P_out)[0]):
        dl = P_out[i,:]
        fStr = '<point id=\"{}\" x=\"{}\" y=\"{}\" z=\"{}\" />\n'.format(i-ct-1,dl[0],dl[1],dl[2])
        outFile.write('                '+fStr)
    outFile.write('            </contour_points>\n')

    for line in inFile:
       outFile.write(line)

    print("Created.")
    inFile.close()
    outFile.close()








    

