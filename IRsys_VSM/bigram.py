# -*- coding: utf-8 -*-
import pickle
import re
import sys

def run(voc,inverted_file,stopword):

	bigram_list=[]

	N=len(inverted_file)

	i=0

	while i < N:
		info=inverted_file[i].strip().split(' ')
		id1=int(info[0])
		id2=int(info[1])
		docCount=int(info[2])
		countSum=0
		oneSum=0
		if id2 != -1:
			if voc[id1] in stopword or voc[id2] in stopword:
				i += docCount +1
				continue
			string=voc[id1].strip()+voc[id2].strip()
			#find useful bigram
			flag=0
			for j in range(i+1,i+docCount+1):
				line=inverted_file[j].strip().split(' ')
				countPerDoc = int(line[1])
				if docCount >= 5:
					if countPerDoc !=1:
						if countPerDoc > 10:
							flag=1
						countSum += countPerDoc
					else:
						oneSum += 1
			if flag==1 or (countSum > oneSum and countSum >= 10):
				bigram_list.append([string,countSum,info[0]+" "+info[1]])
		i += docCount+1

	bigram_list.sort(key = lambda x: x[1], reverse = True)
	'''
	for bigram in bigram_list:
		string = bigram[2]+" "+str(bigram[1])
		print(string)
		print(bigram[0])
	'''
	f=open('bigram.txt','w')
	for bigrams in bigram_list:
		f.write(bigrams[0]+" "+bigrams[2]+"\n")
	f.close()

	return bigram_list


