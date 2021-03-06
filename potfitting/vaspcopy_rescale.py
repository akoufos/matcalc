#!/usr/bin/python

import sys,os,re

def usage():
    print "%s <init_dir> <final_dir> <POSCAR-ratio>"%sys.argv[0].split("/")[-1]
    print "Copies KPOINTS/POSCAR/POTCAR/INCAR from init_dir to final_dir, resizes the POSCAR"

if len(sys.argv)!=4:
    usage()
    exit(0)

initdir=sys.argv[1].rstrip("/")+"/"
finaldir=sys.argv[2].rstrip("/")+"/"
ratio=sys.argv[3]

if os.path.exists(finaldir):
    print "Please delete or rename final directory before running."
    exit(0)
if not os.path.exists(initdir):
    print "Error: Unable to locate initial directory."
    exit(0)

os.mkdir(finaldir)

comm=['cp',initdir+"INCAR",finaldir+"INCAR"]
os.spawnvpe(os.P_WAIT, 'cp', comm, os.environ)
comm=['cp',initdir+"POSCAR",finaldir+"POSCAR"]
os.spawnvpe(os.P_WAIT, 'cp', comm, os.environ)
comm=['cp',initdir+"KPOINTS",finaldir+"KPOINTS"]
os.spawnvpe(os.P_WAIT, 'cp', comm, os.environ)
comm=['cp',initdir+"POTCAR",finaldir+"POTCAR"]
os.spawnvpe(os.P_WAIT, 'cp', comm, os.environ)

#Insert the new ratio into the POSCAR
poscar=open(finaldir+"POSCAR","r").readlines()
poscar[1]=" "+ratio+"\n"
open(finaldir+"POSCAR","w").writelines(poscar)
