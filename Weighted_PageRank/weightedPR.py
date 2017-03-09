import sys
import os
import glob
import numpy as np
from Parser import Parser
from math import *

def WeightedPageRank(nodes, edges, inherent, F, maxIter = 1000):
	#construct out-link weight matrix (dense)
	n=len(nodes)
	epsilon = 0.01/n

	W = np.zeros([n,n])
	for (key,value) in edges.items():
		s,t = key
		W[nodes.index(t), nodes.index(s)]=value
	for i in range (0, n):
		totalW = sum(W[:,i])
		if totalW == 0:
			W[:,i] = 1.0/n
		W[:,i] = W[:,i]/totalW

	#compute weighted page rank
	pagerank=inherent
  	for i in range(0,maxIter):
		p = (1 - F) * inherent + F * np.dot(W, pagerank)
		if max(abs(pagerank-p)) < epsilon:
			break
		pagerank = p

	return pagerank


if __name__ == '__main__':
	#get document list
	file_type = 'html'
	dir_path = sys.argv[1]
	F = float(sys.argv[2])
	path=os.path.join(dir_path,'*.'+file_type)
	files = glob.glob(path)
	fnodes = [file_name.split('/')[-1] for file_name in files]

	#parsing files
	parser = Parser(fnodes, {})
	inherent = []
	for file_name in files:
		parser.set_file(file_name.split('/')[-1])
		with open(file_name,'r') as f:
			read_data = f.read()
			parser.feed(read_data)
			wc = parser.WordCount
			parser.clean()
			#compute different inherent qualities
			inherent.append(log(wc,2))
	
	inherent = np.array(inherent,dtype='double')
	inherent = inherent/sum(inherent)

	#compute WeightedPageRank
	pageRank=WeightedPageRank(parser.nodes,parser.edges,inherent,F)
	for i in range(0,len(pageRank)):
		print '{}	: {}'.format(fnodes[i],pageRank[i])

