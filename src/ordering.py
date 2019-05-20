# -*- coding: utf-8 -*-
"""
Created on Wed May 15 22:20:04 2019

@author: Vincent
"""

import igraph as ig
import time as t

class GraphOrdering:
    def __init__(self, graphName, graph):
        start = t.clock() 
        self.adjacencyDict = {}
        self.orderAdjacencyDict = {}
        self.graphName = graphName
        self.graph = graph
        graphFile = open("../graphs/" + graphName, 'r')
        for line in graphFile:
            vertices = line.replace('\n', '').split(' ')
            self.addEdge(int(vertices[0]), int(vertices[1]))
        graphFile.close()   
        print('Init done in ' + str(t.clock() - start) + ' sec.')
    def addEdge(self, vertex1, vertex2):
        if vertex1 in self.adjacencyDict:
            self.adjacencyDict[vertex1].append(vertex2)
        else:
            self.adjacencyDict[vertex1] = [vertex2]
    def saveReorderAs(self, fileName):
        start = t.clock() 
        data = ''
        for key in self.orderAdjacencyDict:
            for src in self.orderAdjacencyDict[key]:
                for dst in self.orderAdjacencyDict[key][src]:
                    data += str(src) + ' ' + str(dst) + '\n'
        graphFile = open("../graphs/" + fileName, 'w+')
        graphFile.write(data)
        graphFile.close()
        print('Saving new graph done in ' + str(t.clock() - start) + ' sec.')
    def reorder(self):
        start = t.clock() 
        community = self.graph.community_multilevel()
        sizes = community.sizes()
        for i in range(len(sizes)):
            self.orderAdjacencyDict[i] = {}
        members = community.membership
        for i in range(len(members)):
            if i in self.adjacencyDict:
                self.orderAdjacencyDict[members[i]][i] = self.adjacencyDict[i]
        for key in sorted(self.orderAdjacencyDict, key = lambda k: len(self.orderAdjacencyDict[k]), reverse=False):
            self.orderAdjacencyDict[key] = self.orderAdjacencyDict.pop(key)
        for key in self.orderAdjacencyDict:
            for key2 in sorted(self.orderAdjacencyDict[key], key = lambda k: len(self.orderAdjacencyDict[key][k]), reverse=False):
                self.orderAdjacencyDict[key][key2] = self.orderAdjacencyDict[key].pop(key2)
        print('Reorder done in ' + str(t.clock() - start) + ' sec.')

def getGraph(graphName):
    start = t.clock() 
    graph = ig.Graph.Read_Edgelist("../graphs/" + graphName, directed=False)
    time = t.clock() - start
    return graph, time

def getBfsTime(graph):
    start = t.clock() 
    graph.bfs(0)
    return t.clock() - start

def getLouvainTime(graph):
    start = t.clock() 
    graph.community_multilevel()
    return t.clock() - start

def compareLouvainTime(graph1, graph2, n=1):
    time1, time2 = 0, 0
    for i in range(n):
        time1 += getLouvainTime(graph1)
        time2 += getLouvainTime(graph2)
    return time1, time2

def displayGraph(graph):
    layout = graph.layout(layout = "tree")
    display = ig.plot(graph, layout = layout)
    display.show()