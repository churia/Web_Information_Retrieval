import xml.etree.ElementTree as ET
from sklearn.datasets import load_svmlight_file
from sklearn.preprocessing import normalize
import pickle
import numpy as np
import scipy.sparse as sp
import sys



def run(file_vectors,query_vectors,query_id_list,useFeedBack,output,docdir,filelist):
	
	feedbackrate=0.8
	fileCount=len(filelist)
	queryCount=len(query_id_list)
	nonzero=np.unique(query_vectors.indices)

	normfile=normalize(file_vectors, norm='l2', axis=1)
	normfile=normfile[:,nonzero]
	normquery=normalize(query_vectors[:,nonzero], norm='l2', axis=1)

	cosine=normfile*(normquery.transpose())

	ranklist=[]
	for i in range(queryCount):
		scorelist=[]
		for j in range(fileCount):
			scorelist.append((j,cosine[j,i]))
		scorelist.sort(key = lambda x: x[1], reverse = True)
		if useFeedBack == 1:
			scorelist=scorelist[:30]
			docrel=np.array(scorelist)[0]
			weight=sp.csr_matrix(normfile[docrel,:].sum(0)/100)
			normquery[i]=1*normquery[i]+feedbackrate*weight
		else:
			ranklist.append((query_id_list[i],scorelist[:100]))


	if useFeedBack == 1:	
		normquery=normalize(normquery,norm='l2',axis=1)
		newcosine=normfile*(normquery.transpose())

		for i in range(queryCount):
			scorelist=[]
			for j in range(fileCount):
				scorelist.append((j,newcosine[j,i]))
			scorelist.sort(key = lambda x: x[1], reverse = True)
			ranklist.append((query_id_list[i],scorelist[:100]))

	n=0
	out=[]
	for rank in ranklist:
		topic=rank[0]
		scorelist=rank[1]
		for doc in scorelist:
			fileid=doc[0]
			score=doc[1]
		#	if score < 0.15:
		#		break
			path=docdir.replace("CIRB010","")+filelist[fileid].strip()
			f=open(path,"r",encoding="utf-8")
			xml=ET.parse(f).getroot().find("doc")
			f.close()
			doc=xml.find("id").text
			title=xml.find("title").text
			out.append((topic,doc,title))
	#		print(str(topic)+" "+doc+" "+title)

	f=open(output,"w")
	for o in out:
		if o[0]<10:
			t="00"
		else:
			t="0"
		f.write(t+str(o[0])+" "+o[1]+"\n")
	f.close()

        	
