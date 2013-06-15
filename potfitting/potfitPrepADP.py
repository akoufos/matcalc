#!/usr/bin/python

import sys,time
from numpy import *
import scipy.interpolate as interpolate

def nPotentials(x):
    nPhi = x*(x+1)/2.
    nRho = x
    nF = x
    nU = x*(x+1)/2.
    nW = x*(x+1)/2.
    return nPhi,nRho,nF,nU,nW

#interpolate/extrapolate xi points from curve xx,yy
def potExtrap(xi,xx,yy):
    f=interpolate.InterpolatedUnivariateSpline(xx,yy,k=3)
    yi=f(xi)
    return yi

#read in the interpolation points for the X curves
def parse_samples(samplefile):
    sampData=open(samplefile,"r").readlines()
    datax=[[]]
    datay=[[]]
    for line in sampData:
        if len(line)<=1:
            if len(datax[-1])>0:
                datax.append(list())
                datay.append(list())
            continue
        x,y,dumb=line.split()
        datax[-1].append(float(x))
        datay[-1].append(float(y))
    datax.pop(-1)
    datay.pop(-1)
    return datax,datay

def parse_pfend(pfend):
    pfData=open(pfend,"r").readlines()

    #nPots = nPotentials(something)
    #X-data for Phi,Rho,F,U,W
    genXs=lambda x:arange(x[0],x[1]+0.1,(x[1]-x[0])/(x[2]-1))

    l=map(float,pfData[4].split())
    xPhi=genXs(l)
    l=map(float,pfData[5].split())
    xRho=genXs(l)
    l=map(float,pfData[6].split())
    xF=genXs(l)
    l=map(float,pfData[7].split())
    xU=genXs(l)
    l=map(float,pfData[8].split())
    xW=genXs(l)
    pfData=pfData[10:]

    #Y-data
    yPhiDerivs=map(float,pfData[0].split())
    yPhi=array(map(float,pfData[1:1+size(xPhi)]))
    pfData=pfData[2+size(xPhi):]
    yRhoDerivs=map(float,pfData[0].split())
    yRho=array(map(float,pfData[1:1+size(xRho)]))
    pfData=pfData[2+size(xRho):]
    yFDerivs=map(float,pfData[0].split())
    yF=array(map(float,pfData[1:1+size(xF)]))
    pfData=pfData[2+size(xF):]
    yUDerivs=map(float,pfData[0].split())
    yU=array(map(float,pfData[1:1+size(xU)]))
    pfData=pfData[2+size(xU):]
    yWDerivs=map(float,pfData[0].split())
    yW=array(map(float,pfData[1:1+size(xW)]))
    pfData=pfData[2+size(xW):]

    #Insert new points at both ends to account for derivatives
    step=1e-3
    def appendDerivs(x,y,primes,step):
        x=insert(x,0,[x[0]-step])
        y=insert(y,0,[y[0]-primes[0]*step])

        x=insert(x,-1,[x[-1]-step])
        y=insert(y,-1,[y[-1]-primes[1]*step])

        return x,y

    xPhi,yPhi=appendDerivs(xPhi,yPhi,yPhiDerivs,step)
    xRho,yRho=appendDerivs(xRho,yRho,yRhoDerivs,step)
    xF,yF=appendDerivs(xF,yF,yFDerivs,step)
    xU,yU=appendDerivs(xU,yU,yUDerivs,step)
    xW,yW=appendDerivs(xW,yW,yWDerivs,step)

    return [xF,xRho,xPhi,xU,xW],[yF,yRho,yPhi,yU,yW] #return in lammps order!

def usage():
    print "%s <pf_end_??.adp> <output potential> <optional:lammps potential>"%sys.argv[0].split("/")[-1]

if len(sys.argv)<3:
    usage()
    exit(0)

#Reformat potential and write it
#knotx,knoty=parse_samples(pntdata)
knotx,knoty=parse_pfend(sys.argv[1]) #F,rho,phi,u,w
cutx=max(map(max,knotx))
Npnt=1001
dr=cutx/(Npnt-1.)
drho=1./(Npnt-1.)
axx=map(lambda x:x*dr,range(Npnt))
[LRho,LPhi,LU,LW]=[potExtrap(axx,x,y) for i,(x,y) in enumerate(zip(knotx[1:],knoty[1:]))] 
arho=[i*drho for i in range(Npnt)]
LFrho=potExtrap(arho,knotx[0],knoty[0])

#Write element specific data

potential=[ "LAMMPS ADP potential generated by Adam Cadien, George Mason University\n",\
                "%s\n"%time.strftime("%d %b %Y %H:%M:%S", time.localtime()),\
                "-----\n",\
                "1 Ge\n",\
                "%d % 6.6f %d % 6.6f % 6.6f\n"%(Npnt,drho,Npnt,dr,cutx),\
                "32 72.64 0 dummy\n"]

#LAMMPS format
potential+="".join(map(lambda x:"%6.6e\n"%x,LFrho))  
potential+="".join(map(lambda x:"%6.6e\n"%x,LRho))
potential+="".join(map(lambda x:"%6.6e\n"%x,LPhi*axx))
potential+="".join(map(lambda x:"%6.6e\n"%x,LU))
potential+="".join(map(lambda x:"%6.6e\n"%x,LW))
open(sys.argv[2],"w").writelines(potential)

#If the optional arguement for the potfit lammps file is included, plots a comparison of the two
if len(sys.argv)==4:
    #below xcut points are replaced by ixpt and iypt, then interpolated over xx again.
    def cutInterp(xx,yy,xcut):
        #construct cut up arrays
        backx=xx[where(xx>xcut)[0]]
        frontx=xx[where(xx<=xcut)[0]]
        n=len(frontx)
        backy=yy[n:]
        ixpt=[0,1.0,1.5]
        y0=yy[n*2/3]*2
        y1=yy[n*2/3]
        iypt=[y0,y1,yy[n]]
        xxtemp=concatenate([ixpt,backx])
        yytemp=concatenate([iypt,backy])

        #interpolate
        f=interpolate.interp1d(xxtemp,yytemp,3)
        ynew=concatenate([f(frontx)[:n],backy])
        return ynew

    #Parse LAMMPS input Data
    potdata=open(sys.argv[3],"r").readlines()
    #Write element specific data
#    potdata[3]="1 Ge\n"
#    potdata[5]="  32 72.64 0 dummy "+" ".join(potdata[5].split()[4:])+"\n"

    nrho,drho,nr,dr,rcut = map(float,potdata[4].split())
    nr=int(nr)
    nrho=int(nrho)
    rs=array([float(i)*dr for i in range(nr)])
    rhos=array([float(i)*drho for i in range(nrho)])

    F=map(float,potdata[6:6+nrho]) #F(rho) remains unaltered
    Rho=map(float,potdata[6+nrho:6+nr+nrho])
    Phi=map(float,potdata[6+nr+nrho:6+2*nr+nrho])
    U=map(float,potdata[6+2*nr+nrho:6+3*nr+nrho])
    W=map(float,potdata[6+3*nr+nrho:6+4*nr+nrho])
    FRhoPF=array(F)
    RhoPF=array(Rho)
    PhiPF=array(Phi)/(rs+1E-16)
    UPF=array(U)
    WPF=array(W)

    #Plotting
    import pylab as pl
    pl.subplot(231)
    pl.title("Phi(r)")
    pl.scatter(knotx[2],knoty[2])
    yl=pl.ylim()
    pl.plot(axx,LPhi,label="mine")
    pl.plot(rs,PhiPF,label="potfit")
#    pl.ylim(yl)
    pl.legend(loc=0)

    pl.subplot(232)
    pl.title("U(r)")
    pl.scatter(knotx[3],knoty[3])
    yl=pl.ylim()
    pl.plot(axx,LU,label="mine")
    pl.plot(rs,UPF,label="potfit")
#    pl.ylim(yl)
    pl.legend(loc=0)

    pl.subplot(233)
    pl.title("W(r)")
    pl.scatter(knotx[4],knoty[4])
    yl=pl.ylim()
    pl.plot(axx,LW,label="mine")
    pl.plot(rs,WPF,label="potfit")
#    pl.ylim(yl)
    pl.legend(loc=0)

    pl.subplot(234)
    pl.title("Rho(r)")
    pl.scatter(knotx[1],knoty[1])
    yl=pl.ylim()
    pl.plot(axx,LRho,label="mine")
    pl.plot(rs,RhoPF,label="potfit")
    #pl.ylim(yl)
    pl.legend(loc=0)

    pl.subplot(235)
    pl.title("F(rho)")
    pl.plot(arho,LFrho,label="mine")
    pl.plot(rhos,FRhoPF,label="potfit")
    pl.scatter(knotx[0],knoty[0])
    pl.legend(loc=0)

    pl.show()

