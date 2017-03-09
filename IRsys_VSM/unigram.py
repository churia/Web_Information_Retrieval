import pickle

def run(model_dir,stopword_file):

	pun=[]
	f=open(stopword_file)
	for p in f:
		pun.append(p)
	f.close()

	stoplist=[]
	wordlist={}
	f=open(model_dir+"vocab.all",'r')
	vocab=f.readlines()
	for index,line in enumerate(vocab):
		if line in pun:
			stoplist.append(index)
		wordlist[line.strip()]=index
	f.close()

	return wordlist,stoplist
