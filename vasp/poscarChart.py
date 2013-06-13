#!/usr/bin/python

import sys
#mine
import plotRemote as pr

from colors import float2rgb
from scipy import array
from mayavi import mlab
from numpy import linspace,savetxt
import matplotlib.cm as cm
import pylab as pl
from math import sqrt
import re
#mine
from orderParam import *
import poscarIO

orderParams={"CN":  coordinationNumber, \
             "BO":  bondOrientation , \
             "RDF": radialDistribution , \
             "ADF": angleDistribution , \
             "BA":  bondAngleCorr , \
             "SF":  structureFactor, \
             "TET": tetrahedral, \
             "TN":  translational}

def usage():
    print "%s <order parameter> <POSCAR Files (space delim)> <S = save to file instead of plotting>"%sys.argv[0].split("/")[-1]
    print "Order Parameter must be one of:"
    print "   CN  : Coordination Number"
    print "   BO# : Bond Orientation (Q) with l=#"
    print "   RDF : Radial Distribution Function"
    print "   ADF : Angular Distribution Function"
    print "   BA# : Bond Angle Correlation (g)"
    print "   SF  : Structure Factor"
    print "   TET : Tetrahedral"
    print "   TN  : Translational (tao)"
    print ""

if len(sys.argv) < 3:
    usage()
    exit(0)

lval=None
op = sys.argv[1]
if op[:2] in ["BO","BA"]:
    lval=int(op[-1])
    op=op[:2]

orderVals=list()
poscarNames=sys.argv[2:]
saveFlag=False
if poscarNames[-1]=="S":
    poscarNames.pop()
    saveFlag=True

#Sort POSCAR names only based on the numbers in them
try:
    poscarNumbers=map(lambda x:float("".join(re.findall('\d+',x))),poscarNames)
    if len(poscarNumbers) == len(poscarNames):
        poscarNames=zip(*sorted(zip(poscarNames,poscarNumbers),key=lambda x:x[1]))[0]
except ValueError:
    pass


#Gather the order parameters
l=lval
neighbs=None
rcut=None
debug=False
for pn in poscarNames:
    poscar=open(pn,"r").readlines()
    [basis,atypes,atoms,head,poscar] = poscarIO.read(poscar)

    #Get the order parameter
    orderVals.append(orderParams[op](array(atoms),array(basis),l=l,neighbs=neighbs,rcut=rcut,debug=debug))

#======================================================
#                       Plot!
#======================================================
if saveFlag:
    if lval==None:
        lval=""
    for ov,pn in zip(orderVals,poscarNames):
        savetxt(pn+"."+op+str(lval),array(ov).T,delimiter=" ")
    exit(0)

if op not in ["BO","CN","TN","TET"]:
    for ov in orderVals:
        pl.plot(ov[0],ov[1])

if op=="BO":
    print "Average Bond Order <BO%d> ="%lval
    for i,ov in enumerate(orderVals):
        print poscarNames[i],"\t\t",sum(ov)/len(ov)
        vals,bins,dummy = pl.hist(ov,bins=int(sqrt(len(ov)))*5,normed=True,visible=False)#,histtype='step')
        pl.plot(array(bins[:-1]),array(vals),label=poscarNames[i])
    pl.xlabel(r"Bond Order $Q_%d$"%lval)
    pl.ylabel(r"$P ( Q_%d )$"%lval)

elif op=="CN":
    pl.hist(orderVals,bins=range(0,16),normed=True,histtype='bar',align='left',rwidth=0.8)
    pl.xticks(range(min(map(min,orderVals)),max(map(max,orderVals))+1))
    pl.xlabel(r"Coordination Number")
    pl.ylabel(r"P(CN)")
    for i,ov in enumerate(orderVals):
        print "Average CN (%s):"%poscarNames[i],float(sum(ov))/len(ov)

elif op=="RDF":
    pl.xlabel(r"R $( \AA )$")
    pl.ylabel("# Bonds")

elif op=="ADF":
    pl.xlabel(r"$\theta (deg)$")
    pl.ylabel("# Bond Angles")

elif op=="BA":
    pl.xlabel(r"R $( \AA )$")
    pl.ylabel(r"$G_%d ( r )$"%lval)

elif op=="SF":
    pl.xlabel(r"Q $( \AA^{-1})$")
    pl.ylabel(r"S(Q)")

elif op=="TET":
    print "Average Tetrahedral Order <Sg> ="
    for i,ov in enumerate(orderVals):
        print poscarNames[i],"\t\t",sum(ov)/len(ov)

elif op=="TN":
    print "Average Translational Order <tao> ="
    for i,ov in enumerate(orderVals):
        print poscarNames[i],"\t\t",sum(ov)

pl.legend(poscarNames,loc=0)
#Don't plot for some values
if op not in ["TN","TET"]:
    pr.prshow("%s_chart_%s.png"%(sys.argv[1],op))
