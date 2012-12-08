#!/usr/bin/python

#Reads from the CHGCAR_sum generated by the sumchg.pl script
#Given some eV cutoff counts the number of charge cells that are *above* 
#that density and spits out the density as   #cells > chg / total # cells

import sys,operator,os
import pickle
from numpy import *
import scipy
from matplotlib import cm
from matplotlib import ticker
from matplotlib import pyplot as P
import pylab as pl
#mine
import chgcarIO
from colors import float2rgb

def usage():
    print "Usage:"
    print "%s <chgfile> <charge cutoff (eV)> <plotting style: 0,1,2>"%sys.argv[0]
    print "Plotting Styles: 0=none, 1=chg contours, 2=vacancy contours"
    sys.exit()

if not(len(sys.argv) in [3,4]):
    usage()

chgcar = open(sys.argv[1],"r").readlines()
cutev = float(sys.argv[2])
pstyle = int(sys.argv[3])

global dataset
(v1,v2,v3,types,xs,ys,zs,header),gridsz,dataset = chgcarIO.read(chgcar)
#dataset.shape=gridsz[0]*gridsz[1]*gridsz[2]

Tot_pnts = reduce(operator.mul,gridsz)
vol=dot(v1,cross(v2,v3))/Tot_pnts

dataset=vclearout(dataset,avgval*3)
dataset=array([log(i/avgval) for i in dataset])
#dataset is 1d
#dhist=pl.hist(dataset,bins=10000,range=(0,1000),normed=True,histtype='step')[0]
#f=open("CHGDENS_HIST","w")
#pickle.dump(dhist,f)
#f.close()

#Convert the dataset from charge density to vacancy
#def vval(a,b): return 1 if a<b else 0
#vacData=[vval(i,cutev) for i in dataset]
#nvacays=sum(vacData)

#Convert dataset to 3d array
#if pstyle==1:
#    dataset=[clearoutlier(i) for i in dataset]
#    dataset=array(dataset).reshape(gridsz) #[x,y,z]
#elif pstyle==2:
#    dataset=array(vacData).reshape(gridsz) #[x,y,z]

#print "%d Points out of %d Total."%(nvacays,Tot_pnts)
#print "%3.3f%% Vacant"%(nvacays*100.0/Tot_pnts)

x=linspace(0,19,gridsz[0])
y=linspace(0,19,gridsz[1])
X,Y = meshgrid(x,y)

def logplotter(X,Y,z,ticks,colors):
    P.cla()
    return P.contourf(X,Y,z,ticks,colors=colors)#,locator=ticker.LogLocator())

def plotter(X,Y,z):
    P.cla()
    P.contourf(X,Y,z)

def keypress(event):
    global pos,cb,fig,dataset,nticks,ticks,colors,cmap
    if event.key==",":
        pos -= 1
    if event.key==".":
        pos += 10
    if event.key=="a":
        nticks+=1
        ticks=[i/float(nticks) for i in range(nticks)]
        colors=[float2rgb(sqrt(i+1),mic,mxc) for i in range(len(ticks))]
    if event.key=="z":
        nticks-=1
        ticks=[i/float(nticks) for i in range(nticks)]
        colors=[float2rgb(sqrt(i+1),mic,mxc) for i in range(len(ticks))]
    pos=pos%gridsz[0]
    if pstyle==1:
        ax=logplotter(X,Y,dataset[pos,:,:],ticks,colors)
        pl.title("%d Log plot energy density, use < and > to change plots"%pos)
        #P.colorbar(ax,ticks=ticks,drawedges=True)
        cb.update_bruteforce(ax)
    elif pstyle==2:
        plotter(X,Y,dataset[pos,:,:])
        pl.title("%d Vacancy in Red, use < and > to change plots"%pos)
    elif pstyle==3:
        pl.imshow(dataset[pos,:,:],extent=[0,gridsz[0],0,gridsz[1]],cmap=cmap)
    pl.draw()
        
global fig,cb,pos,nticks,ticks,colors,cmap
#ticks=[1e-3,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,25.0,30.0,50.0,70.0,100.0,300.0]
nticks=30
mx=max(dataset.ravel())
mn=min(dataset.ravel())
#ticks=[round(i/float(nticks)*(mx-mn)+mn,2) for i in range(nticks)]
ticks=[i/float(nticks)*(mx-mn)+mn for i in range(nticks)]
mxc=sqrt(len(ticks)+1)
mic=0
colors=[float2rgb(sqrt(i+1),mic,mxc) for i in range(len(ticks))]

#pl.plot([cutev,cutev],[0,0.5],c="black",lw=3.0)
#pl.xlim(0,10)
#pl.xlabel("Charge (eV)")
#pl.ylabel("Count")
#pl.title("Histogram of Charge Density %s"%os.getcwd().split("/")[-1])

if pstyle!=0:
    fig=pl.figure()
    #ax=fig.gca()
    canvas=fig.canvas
    pos=0

    canvas.mpl_connect("key_press_event",keypress)
    if pstyle==1:
        ax=logplotter(X,Y,dataset[pos,:,:],ticks,colors)
        pl.title("%d Log plot energy density, use < and > to change plots"%pos)
        cb=P.colorbar(ax,ticks=ticks[::5],drawedges=True,fraction=0.05)
    elif pstyle==2:
        plotter(X,Y,dataset[pos,:,:])
        pl.title("%d Vacancy in Red, use < and > to change plots"%pos)
    elif pstyle==3:
        cmap=m.hot
        pl.imshow(dataset[pos,:,:],extent=[0,gridsz[0],0,gridsz[1]],cmap=cmap)
P.show()



