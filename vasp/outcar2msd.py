#!/usr/bin/python
import sys
from math import *
from scipy import array,zeros
import pylab as pl
#mine
from meanSquareDist import meanSquareDist
#msdIO

#Calculates mean squared distance

def usage():
    print "Usage: %s <Outcar> "%sys.argv[0].split("/")[-1]

def outcarMeanSquareDisplace(outcarfile):
    outcar=open(outcarfile,"r")
    atoms=list() #atoms[time][atom]

    #Grab ion types
    while True:
        line=outcar.readline()
        if "ions per type" in line:
            break
    atypes=map(int,line.split("=")[1].split())
    Natom=sum(atypes)

    #Grab basis vectors
    while True:
        line=outcar.readline()
        if "direct lattice vectors" in line:
            break
    basis=array([map(float,outcar.readline().split()[:3]) for i in range(3)])
    lengths=array([basis[0][0],basis[1][1],basis[2][2]])

    #Grab atom positions
    count=0
    posit=False
    for line in outcar:
        if posit:
            if "--" in line:
                if len(a)==0:
                    continue
                else:
                    #Analysis
                    atoms.append(array(a))
                    posit=False
            else:
                a.append(map(float,line.split()[:3]))
        elif "POSITION" in line:
            a=list()
            posit=True
            count+=1
    atoms=array(atoms)

    Ntime=len(atoms)
    delT,msd=meanSquareDist(atoms,Natom,Ntime,lengths)
#    for dt in delT:
#        dti=list()
#        for i in range(Ntime-dt):
#            dist_multi_periodic(atoms[i],atoms[i+dt],lengths,ds)
#            dti.append(sum(map(lambda x:x*x,ds)))
#        msd.append(sum(dti)/len(dti))
    print msd[0]
    return delT,msd

if __name__=="__main__":
    if len(sys.argv)<2:
        usage()
        exit(0)
    
    outcarfile=sys.argv[1]
    
    try:
        num=sys.argv[1].split("_")[1]
    except IndexError:
        num=None

    delT,msd=outcarMeanSquareDisplace(outcarfile)

    msdfile="msd.data"

    header="Mean Squared Displacement from %s."%(sys.argv[0])

    print "Writing %s."%msdfile
    pl.plot(msd)
    pl.show()
#    writeAngularPairCor(apcfile,header,bmin,bmax,angs,avgvals)