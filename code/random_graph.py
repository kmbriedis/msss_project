from igraph import Graph
from random import random as rand

def Directed(n, p):
    """Generate directed graph

    Parameters
    ----------
    n : int
        Number of nodes
    p : float
        Probability that 2 nodes are connected.

    Returns
    -------
    igraph.Graph
        Generated graph.

    """
    g = Graph(n, directed = True)
    for i in range(n):
        for j in range(i):
            if rand() < p:
                if rand() > 0.5:
                    g.add_edge(i, j)
                else:
                    g.add_edge(j, i)
    return g

def Directed2(n, p):
    """Generate directed graph

    Parameters
    ----------
    n : int
        Number of nodes
    p : float
        Probability that 2 nodes are connected.

    Returns
    -------
    igraph.Graph
        Generated graph.

    """
    g = Graph(n, directed = True)
    for i in range(n):
        for j in range(n):
            if i != j and rand() < p:
                g.add_edge(i, j)
    return g

def Undirected(n, p):
    """Generate undirected graph

    Parameters
    ----------
    n : int
        Number of nodes
    p : float
        Probability that 2 nodes are connected.

    Returns
    -------
    igraph.Graph
        Generated graph.

    """
    g = Graph(n)
    for i in range(n):
        for j in range(i):
            if rand() < p:
                g.add_edge(j, i)
    return g
