import sys
import unigram
import bigram
import tf_idf
import vectorize
import parse_query
import rank

def exit_with_help(argv):
	print("""\
		options: 
			-r if specified, turn on the relevance feedback
			-i query-file
			-o ranked-list
			-m model-dir (contain: vocab.all,file-list,inverted-file)
			-d NTCIR-dir
""")
	exit(1)

if __name__ == '__main__':

	argc = len(sys.argv)
	argv = sys.argv

	if argc < 2:
		exit_with_help(sys.argv)

	# default options
	feedback = 0
	model_dir = "../model/"
	doc_dir = "../CIRB010/"
	query = "../query/query-test.xml"
	output = "ranked-list"
	stopword_file = "stopword"

	vector_method = 4  #1: tf*idf, 2: norm tf by maxfreq 3:bm25(b) 4: bm25(k,b)
	k=2.5
	b=0.5

	i=1
	while i < argc:
		if argv[i][0] != "-":
			break
		if argv[i] == "-r":
			feedback = 1
		if argv[i] == "-i":
			i = i + 1
			query = argv[i]
		if argv[i] == "-o":
			i = i + 1
			output = argv[i]
		if argv[i] == "-m":
			i = i + 1
			model_dir = argv[i]+"/"
		if argv[i] == "-d":
			i = i + 1
			doc_dir = argv[i]+"/"
		i = i + 1

	f=open(model_dir+'vocab.all','r')
	vocab =f.readlines()
	f.close()
	uniCount=len(vocab)

	f=open(model_dir+'inverted-file','r')
	inverted_index=f.readlines()
	f.close()

	f=open(model_dir+'file-list','r')
	file_list=f.readlines()
	f.close()
	fileCount=len(file_list)

	f=open(stopword_file)
	stopword=f.readlines()
	f.close()

	
	#process file vector space
	bigram_list = bigram.run(vocab,inverted_index,stopword)
	file_TF_matrix, file_IDF_matrix = tf_idf.run(bigram_list,inverted_index,vocab,stopword,uniCount,fileCount)
	file_vector_matrix = vectorize.run(file_TF_matrix,file_IDF_matrix,vector_method,k,b,uniCount,0)

	#process query vector
	query_TF_matrix, query_IDF_matrix,query_id_list = parse_query.run(query,vocab,bigram_list,stopword,uniCount)
	query_vector_matrix = vectorize.run(query_TF_matrix,query_IDF_matrix,vector_method,k,b,uniCount,1)

	#calculate cosine and do ranking
	rank.run(file_vector_matrix,query_vector_matrix,query_id_list,feedback,output,doc_dir,file_list)
