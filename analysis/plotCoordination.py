#!/usr/bin/python

import sys
import pylab as pl
#mine
import coordinationIO

def usage():
    print "Usage: %s <coordination file>"%sys.argv[0].split("/")[-1]

if len(sys.argv)<2:
    usage()
    exit(0)
fname=sys.argv[1]
header,mncn,mxcn,labels,avgs,cnhists=coordinationIO.read(fname)
print header

colors=["red","blue","green","purple","yellow"]
for i in range(len(labels)):
    c=colors[i]
    pl.bar(range(mncn,mxcn),cnhists[i][mncn:mxcn],width=1.0,bottom=0,color=c,alpha=0.75,label=labels[i])
    pl.title(sys.argv[1])
    pl.plot([avgs[i]+0.5,avgs[i]+0.5],[0,max(cnhists[i])],c='black',lw=2,ls="-")

pl.legend(loc=0,title="Max Bond Len:")
pl.xticks(map(lambda x:float(x)+0.5,range(mncn,mxcn)),range(mncn,mxcn))
pl.xlabel("Coordination")
pl.ylabel("Number of Atoms")
pl.show()
