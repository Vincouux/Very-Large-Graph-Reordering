# Very Large Graph - SCIA 2020

The purpose of this project is to highlight the difference in temporal complexity of Louvain algorithm between an unordered and reordered graph. We will try different approaches to reorder the graph.

## Subject

Using the graphs "inet" and "ip".
- Write a reordering algorithm as presented above using a simple BFS, from a random node and from the maxdegree node.
- Test on "inet" / "inetgiant" and "ip" / "ipgiant" the time complexity of Louvain algorithms with time.clock().

## 1 - How to install requirements

### iGraph

```sh
conda install -c conda-forge python-igraph
```
or
```bash
pip install python-igraph
```

### Jupyter Notebook

```bash
pip install jupyter
```
or
```bash
conda install -c anaconda jupyter 
```

### Pandas

```bash
pip install pandas
```
or
```bash
conda install pandas
```

## 2 - Implementation

### 1 - Imports & Graphs (Creating the giants connected component for inet)


```python
import igraph as ig
import time as t
import pandas as pd
```


```python
inet = ig.Graph.Read_Edgelist("../graphs/inet", directed=False)
```

### 2 -  Reordering algorithm


```python
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
```

### 3 -  Testing (i7-9700k / 16Go 2666MHz CL16 / SSD)

#### 1 - Init & Reordering (~47sec)


```python
inetReorder = GraphOrdering('inet', inet)
inetReorder.reorder()
```

    Init done in 13.417700646514163sec.
    Reorder done in 35.84472823166766sec.
    

#### 2 - Saving (~977sec)


```python
inetReorder.saveReorderAs('inet-order')
```

    Saving new graph done in 976.8115150572173sec.
    

#### 3 - Testing (~87sec)


```python
def getGraph(graphName):
    start = t.clock() 
    graph = ig.Graph.Read_Edgelist("../graphs/" + graphName, directed=False)
    time = t.clock() - start
    return graph, time

def getCommunityTime(graph):
    start = t.clock() 
    graph.community_multilevel()
    return t.clock() - start

def getBfsTime(graph):
    start = t.clock() 
    graph.bfs(0)
    return t.clock() - start
```


```python
inet, inetLT = getGraph('inet')
inetOrder, inetOrderLT = getGraph('inet-order')
inetCT = getCommunityTime(inet)
inetOrderCT = getCommunityTime(inetOrder)
inetBFST = getBfsTime(inet)
inetOrderBFST = getBfsTime(inetOrder)


df = pd.DataFrame({'Graph': ['Inet Unordered', 'Inet Reordered'],
                   'Loading Time': [inetLT, inetOrderLT],
                   'Community Time': [inetCT, inetOrderCT], 
                   'BFS Time': [inetBFST, inetOrderBFST]})

print(df)
```

                Graph  Loading Time  Community Time  BFS Time
    0  Inet Unordered      8.704427       36.345318  1.236712
    1  Inet Reordered      6.902874       32.403135  1.092027
    

## 3 - Conclusion

Let G be a graph (V, E) with n = |V| nodes and m = |E| edges. We can say that G is a very large graph (LVG) if n and m are at least some millions. Also, G is a sparse graph if m = O(n). In this analysis, I used inet and ip graphs downloaded on Clémence Magnien's website (https://www-complexnetworks.lip6.fr/~magnien/Diameter/). For all my tests, I used a desktop with i7-9700K, 16Go RAM 2666MHz & CL16 and a SDD for writing edges list files.

For two isomorphic graphs G and G’, any polynomial algorithm on graphs should take the same amount of time. But, when it comes to very large graph with millions or billions of edges, this is not true since two ismorphic graph can be ordered differently on the ram. Therefore, CPU will take slightly more time for an unordered graph traversal since he has to access further memory region.

![originalgraph](https://gitlab.com/Choqs/vlg_scia/raw/master/images/originalgraph.PNG)
![orederedgraph](https://gitlab.com/Choqs/vlg_scia/raw/master/images/orderedgraph.PNG)
<br/>
<cite>Reordering Very Large Graphs for Fun (Lionel Auroux, Marwann Burelle, Robert Erra)</cite>

GraphOrdering class take the graph edges list filename and his iGraph object in parameter (note that your graph edges list file must be in ./graphs/ and be undirected). Initilizer will create an empty adjacency dictionnary and add every edges in it. An empty adjacency dictionnary with community key will also be created and thus for sorting optimization in the reorder() method.
The method reorder() reorder the graph sorting vertices by community size and vertex degree.
The method saveReorderAs() take filename in parametter and save the reordered graph in ./graphs/filename. This method take a lot of time but can be improved with threading depending on the graph file. Since the longest part is the traversal of graph and the creation of the string to be writed, thread can help but they have to keep the order.

I mainly used the inet graph for my tests. My reordering algorithm improved the loading time of the graph, the community detection time and also the BFS time.

The first objective of this work was to prove that it was possible to save computing time by rearranging a graph in RAM. Although the rearrangement algorithm is not efficient and takes a long time, it allows to prove the theory mentioned above.


For the inet graph, my rearrangement algorithm incease community detection speed by 12%,  breadth first search time by 13% and the loading time by 26%. On smaller graph or already arranged graphs, the algorithm does not affect the calculation time. A graph named "medium" with 749 edges is available on the ./graphs folder.

## Credit

Rivière Vincent (rivier_c) - Promo SCIA 2020
