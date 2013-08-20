#!/usr/bin/python
from numpy import *

#Returns a POSCAR file contents in string format, just use writeline to write to file or read using poscarIO.read
def outcar2poscar(outcarF,wantconfig=-1):
    basis=zeros([3,3])
    posi=list()

    outcar = open(outcarF,"r")
    for line in outcar:
        if "ions per type" in line:
            nums=line.split("=")[1].strip()
            Natoms=sum(map(int,nums.split()))
        if "Iteration" in line:
            l=line.split()
            if l[2].strip("(") == "****":
                if l[3].strip(")") == "1":
                    nsteps+=1
            else:
                nsteps=int(line.split()[2].strip("("))

    outcar.close()
    outcar= open(outcarF,"r")

    if wantconfig==-1:
        wantconfig=nsteps
    if wantconfig>nsteps:
        print "Error: outcar2poscar: Requested configuration >%d, the max configurations in OUTCAR."%nsteps
        exit(0)

    wdat="This poscar generated by outcar2poscar.py, from %s configuration #%d\n"%(outcarF,wantconfig)
    wdat+="1.0\n"

    count=0
    while True:
        #Start a new configuration
        line=outcar.readline()
        if len(line)==0:
            break
        if "FORCE on cell" in line:
            count+=1

            if count<wantconfig:
                continue

            while True:
                line=outcar.readline()
                if "direct lattice vectors" in line:
                    line=outcar.readline()
                    basis[0]=map(float,line.split()[0:3])
                    v1=" ".join(line.split()[0:3])
                    line=outcar.readline()
                    basis[1]=map(float,line.split()[0:3])
                    v2=" ".join(line.split()[0:3])
                    line=outcar.readline()
                    basis[2]=map(float,line.split()[0:3])
                    v3=" ".join(line.split()[0:3])
                    break

            while True:
                line=outcar.readline()
                if "POSITION" in line:
                    outcar.readline()
                    while True:
                        line=outcar.readline()
                        atom=linalg.solve(basis.T,array(map(float,line.split()[0:3])))
                        posi.append(" ".join(map(str,atom)))
                        if len(posi)==Natoms:
                            break
                    break
            break
                
    #Generate the rest of the poscar and write it out, make sure to correct for direct output
    if count>=0:
        wdat+=v1+"\n"
        wdat+=v2+"\n"
        wdat+=v3+"\n"
        wdat+=nums+"\n"
        wdat+="Direct\n"
        for i in posi:
            wdat+=i+"\n"
    else:
        raise IOError("Unable to find desired POSCAR in OUTCAR.")
    return wdat

#Returns poscar data and forces in (eV/Angstrom) and stresses (in GPa)
def outcarReadConfig(outcarF,wantconfig=-1):
    nums=""
    types=list()
    basis=zeros([3,3])
    atoms=list()
    forces=list()
    TE=0
    stress=list()
    Natoms=0
    outcar = open(outcarF,"r")

    #Ion types and number of steps
    for line in outcar:
        if "ions per type" in line:
            nums=map(int,line.split("=")[1].split())
            for i in range(len(nums)):
                types+=[i]*nums[i]
            Natoms=sum(nums)
        if "Iteration" in line:
            nsteps=int(line.split()[2].strip("("))
    outcar.close()
    outcar= open(outcarF,"r")

    if wantconfig==-1:
        wantconfig=nsteps
    if wantconfig>nsteps:
        print "Error: outcar2poscar: Requested configuration >%d, the max configurations in OUTCAR."%nsteps
        exit(0)

    count=0
    err=False
    while True:
        #Start a new configuration
        line=outcar.readline()
        if len(line)==0:
            break
        if "FREE ENERGIE OF THE ION-ELECTRON SYSTEM" in line:
            count+=1
            
            if count<wantconfig:
                continue

            #Total Energy
            while True:
                line=outcar.readline()
                if len(line)==0:
                    err=True
                    break
                if "TOTEN" in line:
                    TE=float(line.split("=")[-1].split()[0])
                    break
            #Stresses
            while True:
                line=outcar.readline()
                if len(line)==0:
                    err=True
                    break
                if "in kB" in line:
                    stress=map(lambda x:float(x)/1602.0,line.split()[2:])
                    break
            
            #Lattice Vectors
            while True:
                line=outcar.readline()
                if len(line)==0:
                    err=True
                    break
                if "direct lattice vectors" in line:
                    basis[0]=map(float,outcar.readline().split()[0:3])
                    basis[1]=map(float,outcar.readline().split()[0:3])
                    basis[2]=map(float,outcar.readline().split()[0:3])
                    break
            
            #Atomic Coordinates & Forces
            while True:
                line=outcar.readline()
                if len(line)==0:
                    err=True
                    break
                if "POSITION" in line:
                    outcar.readline()
                    while True:
                        line=outcar.readline()
                        atom=linalg.solve(basis.T,array(map(float,line.split()[0:3])))
                        force=array(map(float,line.split()[3:6]))
                        atoms.append(atom)
                        forces.append(force)
                        if len(atoms)==Natoms:
                            break
                    break
            #All done
            break
    if err:
        print "Error reading OUTCAR, looking for configurations."
        return -1
    return TE,stress,basis,atoms,forces,types
