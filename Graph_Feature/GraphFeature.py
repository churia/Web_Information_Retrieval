import networkx as nx 
import math
import numpy as np

class GraphFeature(object):
    def __init__(self):
        self.Graph = nx.Graph()
        self.Info = {}

    def GetGraphFeatures(self, source, target):
        sn = self.Graph.neighbors(source)
        tn = self.Graph.neighbors(target)

        #commonNeighbors
        common = set(sn) & set(tn)
        commonNeighbors=len(common)

        #jaccardsCoefficient
        jacoef = len(set(sn) & set(tn)) / len(set(sn) | set(tn))

        #adar
        adar = 0
        for z in common:
            adar += 1 / math.log(len(self.Graph.neighbors(z)))

        #shortestPathLength
        if nx.has_path(self.Graph,source,target):
            spl = 1.0 / nx.shortest_path_length(self.Graph, source, target)
        else:
            spl = -1
            
        return [commonNeighbors,jacoef,adar,spl]


    def GetNodeFeatures(self, source, target):
        numerical=[5,15]
        ret=[]
        InfoS=self.Info[source]
        InfoT=self.Info[target]
        print(len(InfoS))
        #54 feature
        for i in range(0,54):
            if InfoS[i]==b'' or InfoT[i]==b'':
                ret.append(0)
                continue
            if i not in numerical:
                items1=InfoS[i].decode().split(' ')
                items2=InfoT[i].decode().split(' ')
                if len(items1)==1 and len(items2)==1:
                    if InfoS[i]==InfoT[i]:
                        ret.append(1)
                    else:
                        ret.append(-1)
                else:
                    count=0
                    for item in items1:
                        if item in items2:
                            count=count+1
                    ret.append(count)
            else:
                ret.append(abs(int(InfoS[i])-int(InfoT[i])))
        return ret

    def FeatureEng(self, GraphFile, NodeProfile, InFile, OutFile):
        print('Building graph')
        with open(GraphFile) as fg:
            fg.readline();  # skip trash
            fg.readline();
            while(True):
                line = str(fg.readline())
                if(line == ''):
                    break
                (s, t) = [int(x) for x in line.split()[:2]]
                self.Graph.add_edge(s, t)
        '''
        print('Reading node info')
        NodeInfo = np.genfromtxt(NodeProfile, dtype = None,delimiter = ',')[1:]
        NodeList = list(NodeInfo[:, 0])
        NodeList = list(map(int, NodeList))
        self.Info =  dict(zip(NodeList, NodeInfo[:, 1:]))
        '''
        print('Computing faetures')
        with open(InFile) as fin:
            lines = fin.readlines()
        with open(OutFile,'w') as fout:
            for line in lines[1:]:
                (l, s, t) = [int(x) for x in line.split(',')[:3]]
                fout.write(str(s) + ', ' + str(t))
                fea1 = self.GetGraphFeatures(s, t)
                #fea2 = self.GetNodeFeatures(s, t)
                for f in fea1:#fea1+fea2:
                    fout.write(', ' + str(f))
                fout.write('\n')
                
if __name__ == '__main__':

    GraphFile='train_edges.txt'
    NodeProfile='pre_nodes_profile.csv'
    InFile='train_edges.txt'
    OutFile='result.txt'
    
    feature = GraphFeature()
    feature.FeatureEng(GraphFile,NodeProfile,InFile,OutFile)