import urlparse
from urllib import urlopen
import robotparser
import os
from bs4 import BeautifulSoup

class Crawler(object):
    #usage: Crawler(url, number, domain, DownDir)#
    def __init__(self, url, number, domain, DownDir):
        self.Start = url
        self.Max = number
        self.Domain = domain
        self.DownDir = DownDir
       
        #parse robots.txt
        self.AgentName = 'churia'
        self.Robot = robotparser.RobotFileParser()
        self.setRobot()

        #set download dir
        if not os.path.exists(self.DownDir):
            os.makedirs(self.DownDir)

        #set list and hashtable for urls
        self.PagesToVisit = [self.Start] #list of urls to crawl, add in BFS order
        self.PagesDict = {self.Start:0} #hashtable of url names

        #start crawling
        self.crawling()

    def setRobot(self):
        # set url for robots.txt parser
        self.Robot.set_url(urlparse.urljoin(self.Domain, 'robots.txt')) 
        self.Robot.read()

    def getLinks(self,baseUrl,htmlString):
        soup = BeautifulSoup(htmlString, 'html.parser')
        for newUrl in soup.find_all('a'):
            link = urlparse.urljoin(baseUrl, newUrl.get('href'))
            #may need to add normalization
            if link not in self.PagesDict:
                self.PagesToVisit.append(link)
                self.PagesDict[link] = 0

    def download(self, name, url, data):
        with open(name,'w') as f:
            try:
               f.write(url+"\n") #save url to file 
               f.write(data.encode("UTF-8"))
            except Exception, e:
                print "can't save file."
        print "download file to",name

    def crawling(self):
        N = 0
        while N < self.Max and self.PagesToVisit != []:
            url = self.PagesToVisit[0]
            self.PagesToVisit = self.PagesToVisit[1:]
            print(N, "Visiting:", url)
            #pass if url is visited.
            if self.PagesDict[url] == 1: 
                print "Visited. Pass"
                continue
            #pass if url not in domain
            if self.Domain not in url: 
                print "Beyond the domain. Pass"
                continue 
            #pass if url not allowed to crawl by robots.txt
            try:
                allow = self.Robot.can_fetch(self.AgentName, url)
                if allow== False: 
                    print "Not allowed to crawl. Pass"
                    continue
            except:
                print "Can't parse url for robots. Pass"
                continue

            #trying to open url
            try:
                response = urlopen(url)
                #pass if not html format file
                if response.info().gettype() != 'text/html':
                    print "Not a HTML link. Pass"
                    continue
                else:
                    data = response.read().decode("UTF-8")
                    self.getLinks(url,data)
                    N = N + 1
                    print "crawled links in total:", len(self.PagesToVisit)
                    name = self.DownDir + str(N) + '.html'
                    self.download(name, url, data)
                    self.PagesDict[url]=1
                    print(" **Success!**")
            except:
                print(" **Visiting failed!**")        

if __name__ == "__main__":
	Crawler("https://en.wikipedia.org/wiki/Algorithm",256,"https://en.wikipedia.org", 'download/')