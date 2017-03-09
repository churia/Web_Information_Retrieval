import pickle
from scipy.sparse import csr_matrix
from sklearn.datasets import dump_svmlight_file
from math import log
import sys

def run(bigram_list,inverted_file,voc,stopword,uniCount,fileCount):

	biCount = uniCount

	bigramDict={}
	for bigram in bigram_list:
		bigramDict[str(bigram[1])+" "+str(bigram[2])]=biCount
		biCount += 1

	N=len(inverted_file)

	file_termfreq_matrix=csr_matrix((fileCount,biCount)).toarray()
	IDF=[0]*biCount

	i=0
	while i < N:
		info=inverted_file[i].strip().split(' ')
		id1=info[0]
		id2=info[1]
		docCount=int(info[2])
		if int(id2) != -1:
			bigram=id1+" "+id2
			if bigram in bigramDict:
				termid = bigramDict[bigram]
			else:
				i += docCount+1
				continue
		else:
			termid = int(id1)
			if voc[termid] in stopword:
				i += docCount+1
				continue
		for j in range(i+1,i+docCount+1):
			line=inverted_file[j].strip().split(' ')
			file_termfreq_matrix[int(line[0]),termid]=int(line[1])

		IDF[termid]=log(float(fileCount)/docCount,2)

		i += docCount+1

	print(file_termfreq_matrix.shape)
	y=[0]*fileCount

	return csr_matrix(file_termfreq_matrix),csr_matrix(IDF)
	

