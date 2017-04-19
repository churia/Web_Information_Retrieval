#!/usr/bin/env python2.7
import cgitb; cgitb.enable()
import cgi
import os
import lucene
import math
 
from java.nio.file import Paths
from java.io import StringReader
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader, Term, MultiFields
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.util import BytesRef
from org.apache.lucene.analysis.standard import StandardTokenizer, StandardFilter
from org.apache.lucene.analysis import LowerCaseFilter, StopFilter, Tokenizer, Token
from org.apache.lucene.analysis.core import StopAnalyzer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute


value  = cgi.FieldStorage()
if value:
	Q = value.getvalue("query")
	K = value.getvalue("number")
	print "Content-Type: text/html\n"
	print "<html><head><title>Mini Search Engine</title></head>\n"
	print "<body><center>\n"
	print "<H2>Results for original query:",Q,"</H2>\n"
	lucene.initVM()
	analyzer = StandardAnalyzer()
	query = QueryParser("text", analyzer).parse(Q)
	dirtry = SimpleFSDirectory(Paths.get("index/"))
	reader = DirectoryReader.open(dirtry)
	searcher = IndexSearcher(reader)
	hits = searcher.search(query, 10)
	r = hits.totalHits #|r(Q)|
	if(r < 1):
		print "Nothing found\n"
	else:
		print "<div align=\"left\"><ol type=\"1\">\n"
		for hit in hits.scoreDocs:
			doc = searcher.doc(hit.doc)
			print "<li> <a href=\"%s\">%s</a></li>" % (doc.get("link").encode('ascii', 'ignore'),doc.get("title").encode('ascii', 'ignore'))
		print "</ol></div>"
		if K and int(K) > 0:
			Qs = [q.replace("text:","") for q in query.toString().split()]
			resultIds = [hit.doc for hit in hits.scoreDocs]
			resultIds.sort()
			Scores = {} #store scores of each word
			for hit in hits.scoreDocs:
				doc = searcher.doc(hit.doc)
				source = doc.get("text")
				sourcewords = source.lower().split()
				l = len(sourcewords) #length of doc
				N = reader.numDocs() #total of docs
				#store neighbors of Qs within 5 words
				Qneighbors = []
				for q in Qs:
					Qpst = [i for i, x in enumerate(sourcewords) if x == q]
					for Qp in Qpst:
						if Qp > 5:
							left = sourcewords[Qp-5:Qp]
						else:
							left = sourcewords[0:Qp]
						right = sourcewords[Qp+1:Qp+6]
						Qneighbors.append(set(left+right))
				#parse and extract all non-stopwords in doc		
				textReader = StringReader(source)
				tokenizer = StandardTokenizer()
				tokenizer.setReader(textReader)
				stream = StandardFilter(tokenizer)
				stream = LowerCaseFilter(stream)
				stream = StopFilter(stream, StopAnalyzer.ENGLISH_STOP_WORDS_SET)
				stream.reset()
				while (stream.incrementToken()):
					word = stream.getAttribute(CharTermAttribute.class_)
					word = word.toString()
					if len(word) <= 1:
						continue
					if word in Qs:
						continue
					#g(W)
					g = reader.docFreq(Term("text",word)) 
					posting = MultiFields.getTermDocsEnum(reader, "text", BytesRef(word))
					z = 0 #z(W,Q)
					c = 0
					for docid in resultIds:
						pid = posting.advance(docid)
						if pid == docid:
							z+=1
							if pid == hit.doc: #count c(W,D)
								c += posting.freq() 
					m = len(Qneighbors)
					f = 0
					for Qn in Qneighbors:
					    if word in Qn:
					        f+=1
					y = max(0,float(z)/r-2*float(g)/N)
					cl = math.sqrt(float(c)/l)
					if m == 0:
						fm = 0
					else:
						fm = math.sqrt(float(f)/m)
					s = fm + y*cl
					if word not in Scores:
					    Scores[word] = s
					else:
					    Scores[word] += s
			# sort words by scores
			Scores=sorted(Scores.items(), key=lambda x: x[1],reverse=True)
			Qstr = "" 
			for i in range(0,int(K)):
				key, value = Scores[i]
				Qstr += str(key)+" "
			print "<H2>Results for expanded query: [ %s ] + [ %s] </H2>\n" % (Q,Qstr)
			newQuery = QueryParser("text", analyzer).parse(Q+" "+Qstr)
			hits = searcher.search(newQuery, 10)
			print "<div align=\"left\"><ol type=\"1\">\n"
			for hit in hits.scoreDocs:
				doc = searcher.doc(hit.doc)
				print "<li> <a href=\"%s\">%s</a></li>" % (doc.get("link").encode('ascii', 'ignore'),doc.get("title").encode('ascii', 'ignore'))
			print "</ol></div>"
	print "</center></body></html>\n"
else:
	print "Query has not received!"
	f = open('index.html', 'r'); s = f.read(); f.close()
	print "Content-Type: text/html\n"
	print s
