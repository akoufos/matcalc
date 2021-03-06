#!/usr/bin/python
import sys

#Write the x/y data to a chi file
def writechi(xs,ys,filename):
    import datetime
    data="This chi-file was generated by %s. %s\n"%(sys.argv[0],datetime.date.today())
    data+="2-Theta Angle (Degrees)\n"
    data+="Intensity\n"
    data+="\t%d\n"%len(xs)
    for i in range(len(xs)):
        data+="%e  %e\n"%(xs[i],ys[i])
    open(filename,"w").write(data)

#Reads in the chi file
def readchi(filename):
    f=open(filename,'r').readlines()
    xxs=list()
    yys=list()
    for line in f[4:]:
        a=[float(i) for i in line.split()]
        xxs.append(a[0])
        yys.append(a[1])
    return xxs,yys
