import sys
import pickle
from sklearn.datasets import dump_svmlight_file
from sklearn.datasets import load_svmlight_file
from scipy import sparse
import numpy as np
'''
method1=TF*IDF;
method2=normalize TF with maxFreq;
method3=normalize TF with Okapi/BM25, (b);
method4=normalize TF with Okapi/BM25, (k,b);
'''

method=4
k=1.5
b=0.75

def run(TF_matrix,IDF,method,k,b,uniCount,query):

	fileCount,featureCount=TF_matrix.shape

	if method == 1:
		TF_matrix.data*=IDF.toarray()[0][TF_matrix.indices]

	unigram_matrix = TF_matrix[:,:uniCount]
	if method == 2:
		#calculate maxFreq
		uniMaxFreq =unigram_matrix.max(axis=1).toarray() #one of the doc(43024) is empty so result in zero
		if not query and uniMaxFreq[43024]==0:
			uniMaxFreq[43024]=1
		bigram_matrix = TF_matrix[:,uniCount:]
		biMaxFreq =bigram_matrix.max(axis=1).toarray()
		if not query and biMaxFreq[43024]==0:
			biMaxFreq[43024]=1

		#construct vector
		unigram_matrix=unigram_matrix.tocoo()
		unigram_matrix.data/=uniMaxFreq[unigram_matrix.row].reshape(len(unigram_matrix.data),)
		bigram_matrix=bigram_matrix.tocoo()
		bigram_matrix.data/=biMaxFreq[bigram_matrix.row].reshape(len(bigram_matrix.data),)
		TF_matrix = sparse.hstack([unigram_matrix,bigram_matrix])
		TF_matrix.data = TF_matrix.data*0.5+0.5
		TF_matrix.data*=IDF.toarray()[0][TF_matrix.col]

	if method == 3:
		#calculate doclen and avgdoclen
		doclens=unigram_matrix.sum(axis=1)
		avglen=doclens.mean()

		#construct vector
		tmp=1-b+b*doclens/avglen
		TF_matrix=TF_matrix.tocoo()
		TF_matrix.data/=np.array(tmp[TF_matrix.row]).reshape(len(TF_matrix.data),)
		TF_matrix.data*=IDF.toarray()[0][TF_matrix.col]

	if method == 4:
		#calculate doclen and avgdoclen
		doclens=unigram_matrix.sum(axis=1)
		avglen=doclens.mean()

		#construct vector
		TF_matrix=TF_matrix.tocoo()
		tmp1 = TF_matrix*(k+1)
		tmp2 = k*(1-b+b*doclens/avglen)
		TF_matrix.data += np.array(tmp2[TF_matrix.row]).reshape(len(TF_matrix.data),)
		TF_matrix.data = tmp1.data/TF_matrix.data
		TF_matrix.data*=IDF.toarray()[0][TF_matrix.col]

	return TF_matrix.tocsr()

