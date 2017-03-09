# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pickle
from scipy import sparse
from sklearn.datasets import dump_svmlight_file
from math import log
import numpy as np


def run(input,vocab,bigram_list,stopwordlist,uniCount):
	titleScore = 5
	docScore = 2

	stopword=[]
	for word in stopwordlist:
		stopword.append(word.strip())

	unigram={}
	for index,line in enumerate(vocab):
		unigram[line.strip()]=index

	bigram={}
	for index,b in enumerate(bigram_list):
		bigram[b[0].strip()]=index

	featureCount=uniCount+len(bigram_list)
	print(featureCount)

	f=open(input,"r",encoding="utf-8")
	xml=ET.parse(f).getroot()
	f.close()

	topics= xml.findall("topic")

	query_tf_matrix=sparse.csr_matrix((len(topics),featureCount)).toarray()
	IDF=np.array([0]*featureCount)

	queryCount=len(topics)

	y=[]
	for n in range(0,queryCount):
		print(n)
		topic=topics[n]
		idf=np.array([0]*featureCount)
		number=topic.find("number").text.strip().split("ZH")[1]
		y.append(int(number))
		title=topic.find("title").text.strip()
		question=topic.find("question").text.strip()
		narrative=topic.find("narrative").text.split("。")[0]
		concepts=topic.find("concepts").text.strip()
		doc=question+" "+narrative+" "+concepts
		doc = doc.replace("查詢","").replace("相關文件內容","").replace("應","").replace("包括","").replace("應說明","")

	#	flag=np.array([1]*len(title))
		for i in range(len(title)-1):
			if title[i] not in stopword  and title[i] in unigram:
				if i==len(title)-1:
					if title[i+1] not in stopword and title[i+1] in unigram:
						query_tf_matrix[n,unigram[title[i+1]]]+=titleScore
						idf[unigram[title[i+1]]]=1
				query_tf_matrix[n,unigram[title[i]]]+=titleScore
				idf[unigram[title[i]]]=1
			if title[i:i+2] in bigram:
				query_tf_matrix[n,bigram[title[i:i+2]]+uniCount]+=titleScore*1.5
				idf[bigram[title[i:i+2]]+uniCount]=1
	#			flag[i]=0
	#			flag[i+1]=0
		'''
		if len(np.nonzero(flag))>0:
			for i in np.nonzero(flag)[0]:
				print(title[i])
		'''
	#	flag=np.array([1]*len(doc))
		for i in range(len(doc)-1):
			if doc[i] not in stopword and doc[i] in unigram:
				if i==len(doc)-1:
					if doc[i+1] not in stopword and doc[i+1] in unigram:
						query_tf_matrix[n,unigram[doc[i+1]]]+=docScore
						idf[unigram[doc[i+1]]]=1
				query_tf_matrix[n,unigram[doc[i]]]+=docScore
				idf[unigram[doc[i]]]=1
			if doc[i:i+2] in bigram:
				query_tf_matrix[n,bigram[doc[i:i+2]]+uniCount]+=docScore*1.5
				idf[bigram[doc[i:i+2]]+uniCount]=1
	#			flag[i]=0
	#			flag[i+1]=0
		'''
		if len(np.nonzero(flag))>0:
			for i in np.nonzero(flag)[0]:
				print(doc[i])
		'''
		IDF += idf

	for i in np.nonzero(IDF)[0]:
		idf=log(float(queryCount)/IDF[i],2)
		IDF[i]=idf

	return sparse.csr_matrix(query_tf_matrix),sparse.csr_matrix(IDF),y

