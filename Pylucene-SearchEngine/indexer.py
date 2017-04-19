import lucene
import os
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from bs4 import BeautifulSoup

class Indexer(object):
	def __init__(self, docDir,indexDir,analyzer):
	#set index dir
		if not os.path.exists(indexDir):
			os.makedirs(indexDir)
		self.indexDir = SimpleFSDirectory(Paths.get(indexDir))
		self.docDir = docDir

		self.analyzer = LimitTokenCountAnalyzer(StandardAnalyzer(),1048576)
		writerConfig = IndexWriterConfig(self.analyzer)
		writerConfig.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
		self.writer = IndexWriter(self.indexDir, writerConfig)
		self.indexing()

	def indexing(self):
		t1 = FieldType()
		t1.setStored(True)
		t1.setTokenized(False)
		t1.setIndexOptions(IndexOptions.NONE)

		t2 = FieldType()
		t2.setStored(True)
		t2.setTokenized(True)
		t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

		for filename in os.listdir(self.docDir):
			if filename.endswith('.html') or filename.endswith ('.htm'):
				with open(os.path.join(self.docDir,filename)) as f:
					url = f.readline().strip()
					htmlString= f.read()
					#remove HTML markup
					soup = BeautifulSoup(htmlString, 'html.parser')
					# kill all script and style elements
					for script in soup(["script", "style"]):
						script.extract()    # rip it out
					# get text
					text = soup.get_text()
					# break into lines and remove leading and trailing space on each
					lines = (line.strip() for line in text.splitlines())
					# break multi-headlines into a line each
					chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
					# drop blank lines
					text = '\n'.join(chunk for chunk in chunks if chunk)
					#text = soup.get_text().strip() 
					title = soup.title.string
					#print text
				doc = Document()
				doc.add(Field("link", url,t1))
				doc.add(Field("title",title,t1))
				doc.add(Field("text", text, t2))
				self.writer.addDocument(doc)
				print "index document", filename 

		self.writer.commit()
		self.writer.close()

if __name__ == '__main__':
	lucene.initVM(vmargs=['-Djava.awt.headless=true'])
	print 'lucene', lucene.VERSION
	try:
		Indexer('download/','index', StandardAnalyzer)
	except Exception, e:
		print "Failed:", e