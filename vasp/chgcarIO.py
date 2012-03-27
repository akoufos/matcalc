#!/usr/bin/python

from numpy import matrix,linalg
from scipy import *
import operator
#mine
from poscarIO import readposcar


#Multiplies by volume to get absolute Charge
def readchgcar(chgcar):
    v1,v2,v3,types,xs,ys,zs,header,chgcar=readposcar(chgcar)
    poscardata=(v1,v2,v3,types,xs,ys,zs,header)

    chgcar.pop(0)
    gridsz=[int(i) for i in chgcar.pop(0).split()]

    Tot_pnts = reduce(operator.mul,gridsz)
    vol=dot(v1,cross(v2,v3))/Tot_pnts

    chgdata=[float(i)*vol for i in "".join(chgcar).split()[:Tot_pnts]]

    return poscardata,gridsz,chgdata
