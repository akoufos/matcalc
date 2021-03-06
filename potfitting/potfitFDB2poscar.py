#!/usr/bin/python
import sys
from numpy import *
import scipy.linalg
#mine
import poscarIO

if len(sys.argv)<2:
    print "Usage:"
    print sys.argv[0].split("/")[-1]+" <force database file> <config#> <output POSCAR>"
    print "Parses the force database and generates a POSCAR with the proper information from the configuration given."
    exit(0)

forcedb = open(sys.argv[1],"r")
confignum = int(sys.argv[2])

count=0
done=0
while True:
    #Start a new configuration
    line=forcedb.readline()
    if len(line)==0:
        break
    if not("#N" in line):
        print "Error expecting the first line of a configuration to start with \"#N."
        print "Got: \""+line+"\" instead."
        print "Exiting."
        exit(0)
    
    #Print the header
    print "Header"
    head = line
    print line

    #Number of atoms in configuration
    natom = int(line.split()[1])
    msg = line.split("=")[1].split()[1]

    #Element types
    line=forcedb.readline()
    if line[:2]=="#C":
        elems=line[2:].split()
        line=forcedb.readline()

    #Bounding box vectors
    boundx=" ".join(line.split()[1:])
    bndx=[float(i) for i in boundx.split()]

    line=forcedb.readline()
    boundy=" ".join(line.split()[1:])
    bndy=[float(i) for i in boundy.split()]

    line=forcedb.readline()
    boundz=" ".join(line.split()[1:])
    bndz=[float(i) for i in boundz.split()]

    basis=[bndx,bndy,bndz]
    vol=round(dot(bndx,cross(bndy,bndz)),2)

    #Cohesive energy
    line=forcedb.readline()
    Ecoh=line.split()[1]

    #Weights (ignore)
    line=forcedb.readline()
    if line[:2]=="#W":
        line=forcedb.readline()

    #Stresses
    stress=" ".join(line.split()[1:])
 
    #Atomic locations and forces.
    forcedb.readline() #The #F
    atype=[0]*natom
    ax=[0.0]*natom
    ay=[0.0]*natom
    az=[0.0]*natom
    afx=[0.0]*natom
    afy=[0.0]*natom
    afz=[0.0]*natom
    for i in range(natom):
        line=forcedb.readline().split()
        atype[i]=int(line[0])
        [ax[i],ay[i],az[i],afx[i],afy[i],afz[i]]=[float(j) for j in line[1:7]]

    if(count==confignum):
        pcar=sys.argv[3]
        poscarIO.write(pcar,array(basis),zip(ax,ay,az),atype,head)

        """
        wrt=pcar+" "+msg+"\n"
        wrt+="1.0\n"
        wrt+=boundx+"\n"
        wrt+=boundy+"\n"
        wrt+=boundz+"\n"
        
        types=[atype.count(u) for u in set(atype)]
        wrt+=" ".join(map(str,types))+"\n"#type information
        wrt+="Direct\n"

        a=array([bndx,bndy,bndz])
        for b in zip(ax,ay,az):
            x=linalg.solve(a.transpose(),b)
            wrt+="%9.9f %9.9f %9.9f\n"%(x[0],x[1],x[2])
        ofil=open(pcar,"w")
        ofil.write(wrt)
        ofil.close()
        """
        done=1
        break

    #Statistics
    count+=1
    if done==1: break

print "Wrote to %s"%sys.argv[3]

