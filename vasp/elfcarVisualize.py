#!/usr/bin/python

#Reads from the CHGCAR_sum generated by the sumchg.pl script
#Given some eV cutoff counts the number of charge cells that are *above* 
#that density and spits out the density as   #cells > chg / total # cells

import sys,operator,os
import pickle
from numpy import *
from matplotlib import ticker
import matplotlib
import subprocess
#mine
from elfcarIO import readelfcar
from colors import float2rgb

def usage():
    print "Usage:"
    print "%s <elfcarfile> <plotting style: 0(+image name),1,2,3,4> <optinal: log (take log of data)>"%sys.argv[0].split("/")[-1]
    print "Plotting Styles: 0=save an image, 1=chg contours, 2=make a bunch of plots for a movie,\n3=chg contours with atoms, 4=make a bunch of plots for a movie with spheres"
    exit(0)

if len(sys.argv) < 3:
    usage()

elfcar = open(sys.argv[1],"r").readlines()
pstyle = int(sys.argv[2])

#If saving a picture, assume remote use which requires Agg
if pstyle==0:
    fname=sys.argv[3]
    matplotlib.use("Agg")
else:
    from matplotlib import pyplot as P
import pylab as pl

global dataset
(v1,v2,v3,types,cxs,cys,czs,header),gridsz,dataset = readelfcar(elfcar)

Npnts = reduce(operator.mul,gridsz)

#VASP outputs CHGCAR/ELFCARs in the order Z,Y,X.  Transfrom this to X,Y,Z
dataset=array(dataset).reshape(list(reversed(gridsz))) #[x,y,z]
dataset=dataset.swapaxes(0,2)
#dataset=log(dataset)
global atoms,atomcolors,atombounds
#Ge: 1.22 
#Sb: 1.4
#Te: 1.4
#Au: 1.35
#Cu: 1.4
#Ce: 1.8
radii=[0.7]
acolors=[(0.1,0.1,0.1),(0.5,0.5,0.5),(0.9,0.9,0.9)]
atomradii=list()
atomcolors=list()
for i in range(len(types)):
    t=types[i]
    atomradii+=[radii[i]]*t
    atomcolors+=[acolors[i]]*t
atoms=zip(cxs,cys,czs,atomradii)
atombounds=array([[zpos-r,zpos+r] for zpos,r in zip(czs,atomradii)])

x=linspace(0,v1[0],gridsz[0])-v1[0]/gridsz[0]/2.
y=linspace(0,v2[1],gridsz[1])-v2[1]/gridsz[1]/2.
global zsize
zsize=v3[2]

X,Y = meshgrid(x,y)
cdir=os.getcwd().split("/")[-1]

def plotspheres(zpos,atombounds,atoms,atomcolors):
    for i,bounds in enumerate(atombounds):
        cirs=list()
        if (zpos > bounds[0] and zpos < bounds[1]) or zpos < bounds[1]-v3[2] or zpos > bounds[0]+v3[2]:
            x=atoms[i][0]
            y=atoms[i][1]
            z=atoms[i][2]
            
            d=z-zpos
            if bounds[0] < 0 and zpos>v3[2]/2:
                d+=v3[2]
            elif bounds[1] > v3[2] and zpos<v3[2]/2:
                d-=v3[2]
            r=sqrt(atoms[i][3]**2-d**2)

            cirs.append( pl.Circle((x,y),radius=r, fc='None' , color=atomcolors[i], linewidth=2))

            if x+r > v1[0]:
                cirs.append(pl.Circle((x-v1[0],y), radius=r, fc='None' , color=atomcolors[i], linewidth=2))
            if x-r < 0:
                cirs.append(pl.Circle((x+v1[0],y), radius=r, fc='None' , color=atomcolors[i], linewidth=2))
            if y+r > v2[1]:
                cirs.append(pl.Circle((x,y-v2[1]), radius=r, fc='None' , color=atomcolors[i], linewidth=2))
            if y-r < 0:
                cirs.append(pl.Circle((x,y+v2[1]), radius=r, fc='None' , color=atomcolors[i], linewidth=2))

            if x+r > v1[0] and y+r > v2[1]:
                cirs.append( pl.Circle((x-v1[0],y-v2[1]), radius=r, fc='None' , color=atomcolors[i], linewidth=2))
            if x+r > v1[0] and y-r < 0:
                cirs.append(pl.Circle((x-v1[0],y+v2[1]), radius=r, fc='None' , color=atomcolors[i],linewidth=2))
            if x-r < 0 and y+r > v2[1]:
                cirs.append(pl.Circle((x+v1[0],y-v2[1]), radius=r, fc='None' , color=atomcolors[i],linewidth=2))
            if x-r < 0 and y-r < 0:
                cirs.append(pl.Circle((x+v1[0],y+v2[1]), radius=r, fc='None' , color=atomcolors[i],linewidth=2))
            for cir in cirs:
                pl.gca().add_patch(cir)

def image_spheres(bounds,z,pos,atombounds,atoms,atomcolors):
    pl.cla()
    plotspheres(pos,atombounds,atoms,atomcolors)
    pl.imshow(flipud(z),extent=bounds,vmin=0,vmax=1)

def logplotter_spheres(X,Y,z,ticks,colors,pos,atombounds,atoms,atomcolors):
    pl.cla()
    pl.contourf(X,Y,z.T,ticks,colors=colors,locator=ticker.LogLocator())
    pl.contour(X,Y,z.T,ticks,colors="black",linestyles='dotted')
    plotspheres(pos,atombounds,atoms,atomcolors)
    pl.tick_params(axis='both',bottom='off',left='off',labelbottom='off',labelleft='off',right='off',top='off')

def logplotter(X,Y,z,ticks,colors):
    pl.cla()
    pl.contourf(X,Y,z.T,ticks,colors=colors,locator=ticker.LogLocator())
    pl.contour(X,Y,z,ticks,colors="black")#colors)#,locator=ticker.LogLocator())
    pl.tick_params(axis='both',bottom='off',left='off',labelbottom='off',labelleft='off',right='off',top='off')

def plotter(X,Y,z):
    pl.cla()
    pl.contourf(X,Y,z.T)

def keypress(event):
    global pos,fig,dataset,ticks,colors,atombounds,atoms,atomcolors,zsize
    if event.key==",":
        pos -= 1
    if event.key==".":
        pos += 10
    pos=pos%gridsz[2]
    if pstyle==1:
        logplotter(X,Y,dataset[:,:,pos],ticks,colors)
    elif pstyle==3:
        logplotter_spheres(X,Y,dataset[:,:,pos],ticks,colors,pos*zsize/gridsz[2],atombounds,atoms,atomcolors)
    elif pstyle==5:
        image_spheres([0,v1[0],0,v2[1]],dataset[:,:,pos],pos*zsize/gridsz[2],atombounds,atoms,atomcolors)
    pl.title("%d ELF, use < and > to change plots\n%s"%(pos,cdir))
    pl.draw()
        
global fig,pos,ticks,colors

# Figure out the min/max values for coloring the data, apply log if requested
if len(sys.argv) ==4:
    #take log of the data
    if sys.argv[3]=="log":
        dataset=log(dataset)
        chgfactor=dataset.max()
        ticks=[(i-1)/20.*chgfactor for i in range(20)]
    else:
        print "Error Arguement 3 not recognized."
        exit(0)
elif "AECCAR" in sys.argv[1] or "CHGCAR" in sys.argv[1]:
    #no log, but automate the calculation of min/max color values
    mxd=float(dataset.sum()/Npnts)
    nbins=1000
    bins=array(range(nbins))*mxd/nbins
    indeces = list(bincount( digitize(dataset.ravel(),bins) ))
    st=False
    for i,val in enumerate(indeces):
        if st==False and val!=0:
            j=i
            st=True
        if st==True and val==0:
            break
    cutoff = sum(indeces[j:])*0.01
    bigindex = where(indeces[j:] > cutoff)[0][-1]+j
    chgfactor = (bigindex+1) * mxd/nbins
    
    ticks=[(i-1)/20.*chgfactor for i in range(20)]
else:
    ticks=[i/20. for i in range(20)]

mxc=sqrt(len(ticks)+1)
mic=0
colors=[float2rgb(sqrt(i+1),mic,mxc) for i in range(len(ticks))]

if pstyle!=0:
    fig=pl.figure()
    ax=fig.add_subplot(111,aspect='equal',autoscale_on=False)
    canvas=fig.canvas
    pos=0

    
    canvas.mpl_connect("key_press_event",keypress)
    if pstyle==1:
        logplotter(X,Y,dataset[:,:,pos],ticks,colors)
        pl.colorbar(ticks=ticks,drawedges=True)
    elif pstyle==2:
        for i in range(gridsz[0]):
            logplotter(X,Y,dataset[:,:,i],ticks,colors)
            if i==0:
                pl.colorbar(ticks=ticks,drawedges=True)
            for p in range(2):
                pl.savefig("elfplot%3.3d.png"%(i*2+p))
    elif pstyle==3:
        logplotter_spheres(X,Y,dataset[:,:,pos],ticks,colors,pos*zsize/gridsz[2],atombounds,atoms,atomcolors)
        #pl.colorbar(ticks=ticks,drawedges=True)
    elif pstyle==4:
        for i in range(gridsz[0]):
            logplotter_spheres(X,Y,dataset[:,:,i],ticks,colors,i*zsize/gridsz[2],atombounds,atoms,atomcolors)
            if i==0:
                pl.colorbar(ticks=ticks,drawedges=True)
            for p in range(2):
                pl.savefig("elfplot%3.3d.png"%(i*2+p))
    elif pstyle==5:
        image_spheres([0,v1[0],0,v2[1]],dataset[:,:,i],i*zsize/gridsz[2],atombounds,atoms,atomcolors)
        P.colorbar()
    pl.title("%d Log plot ELF, use < and > to change plots\n%s"%(pos,cdir))
    pl.show()
else:
    logplotter_spheres(X,Y,dataset[:,:,0],ticks,colors,0*zsize/gridsz[2],atombounds,atoms,atomcolors)
    pl.savefig(fname)




