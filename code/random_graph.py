from igraph import Graph
from random import random as rand

def Directed(n, p):
    g = Graph(n, directed = True)
    for i in range(n):
        for j in range(i):
            if rand() < p:
                if rand() > 0.5:
                    g.add_edge(i, j)
                else:
                    g.add_edge(j, i)
    return g
