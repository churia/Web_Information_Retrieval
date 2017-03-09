import sys
from scipy import sparse
import numpy as np
import getopt

d=0.85
epsilon=0.000001
maxIter=200

#-----------parse command--------------
optlist,inputfile=getopt.getopt(sys.argv[1:],'d:e:i:o:')
output=inputfile[0]+".pagerank"
for opt,arg in optlist:
	if '-d' in opt:
		d=float(arg)
	elif '-e' in opt:
		epsilon=float(arg)
	elif '-i' in opt:
		maxIter=int(arg)
	elif '-o' in opt:
		output=arg
	else:
		pass

#-------------read file-----------------
f=open(inputfile[0])

first=f.readline().strip().split(" ")
max_node=int(first[1])+1

lines=f.readlines()
f.close()

indptr = [0]
index = []
data = []

total_index=[i for i in range(0,max_node)]

count=0
for line in lines:
	strs=line.strip().split(":")
	node=int(strs[0])
	while node!=count:
		indptr.append(len(index))
		count+=1
	strs=strs[1].split(" ")
	o=1/int(strs[0])
	for i in range(1,len(strs)):
		data.append(o)
		index.append(int(strs[i]))
	indptr.append(len(index))
	count+=1

#create max_node*max_node sparse matrix
AT=sparse.csc_matrix((data,index,indptr),dtype=float)
shape=AT.shape
if shape[0] < max_node:
	tmp=sparse.csc_matrix((max_node-shape[0],shape[1]))
	AT=sparse.vstack([AT,tmp])
	shape=AT.shape
if shape[1] < max_node:
	tmp=sparse.csc_matrix((max_node,max_node-shape[1]))
	AT=sparse.hstack([AT,tmp])
zero_index=np.setdiff1d(total_index,AT.nonzero()[1])

#-------------power iteration------------
P=np.ones((max_node,1))
P[0]=0
for i in range(0,maxIter):
	new=AT*P+1/(max_node-2)*sum(P[zero_index])
	new[zero_index]-=1/(max_node-2)*P[zero_index]
	newP=1-d+d*new
	newP[0][0]=0
	if np.linalg.norm(newP-P) < epsilon:
		break
	else:
		P=newP

#-------------save output----------------
f=open(output,'w')
for i in range(1,max_node):
	s="%.6f" %(P[i][0])
	f.write(str(i)+":"+s+"\n")
f.close()
