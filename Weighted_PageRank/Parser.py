from HTMLParser import HTMLParser

class Parser(HTMLParser):
	def __init__(self, nodes, edges):
		self.reset()
		self.clean()
		self.nodes = nodes
		self.edges = edges

	def clean(self):
		self.WordCount = 0
		self.flag = 0
		self.name = ''

	def handle_starttag(self, tag, attrs):
		if tag in ['H1', 'H2', 'H3', 'H4', 'em','b']:
			#if links are in the special scope, weight+1, assume no nested
			self.flag = 1
		if tag in ['a','A']:
			for (key,value) in attrs:
				if key == 'href':
					if value in self.nodes:
						if (self.name, value) in self.edges:
							#counted weight
							self.edges[(self.name,value)] += 1 + self.flag
						else:
							self.edges[(self.name,value)] = 1 + self.flag
			self.flag = 0

	def handle_data(self, data):
		words = data.split()
		self.WordCount += len(words)

	def set_file(self, file_name):
		self.name = file_name
		print 'parsing ', self.name
