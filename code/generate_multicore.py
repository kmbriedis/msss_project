"""
    Written by Kārlis Mārtiņš Briedis
"""
import argparse
import time
import numpy as np
from generate_graph import GraphGenerator
from igraph import Graph
import os
from multiprocessing import Process, Pool, cpu_count


def Generate_single(fname, N, targets, max_iter = 100000):
    """Generate single graph, made for running on its own process

    Parameters
    ----------
    fname : string
        Filename where to save graph
    N : int
        Size of graph.
    targets : array
        Array of targets for graph to meet.
    max_iter : type
        Maximum number of iterations.

    """
    gen = GraphGenerator(targets, verbose = False)
    [g, energy] = gen.simulated_annealing(Graph(N), max_iter = max_iter)
    g.write_pickle(fname)


def Generate_multicore(sets, N, each_N):
    """Generate multiple graphs using multiple cores

    Parameters
    ----------
    sets : array
        Targets and paths for graph to generate.
    N : int
        Size of each graph.
    each_N : int
        Number of different of graphs for each type.

    """
    start_time = time.time()

    print("Generating cluterings")
    print("%i cores available" % cpu_count())

    graphs = []
    for i in range(len(sets)):
        [path, targets] = sets[i]
        os.makedirs(path, exist_ok = True)
        for j in range(each_N):
            fname = "%s/%i.graph" % (path, j)
            graphs.append((fname, N, targets))

    pool = Pool()
    rs = pool.starmap_async(Generate_single, graphs)

    pool.close()
    while (True):
      if (rs.ready()): break
      remaining = rs._number_left
      print("Waiting for %i tasks to complete..." % (remaining), end="\r")
      time.sleep(30)

    print("\r\nDone, took %i seconds" % (time.time() - start_time))


def Generate_clustering(N, d, cluster_N, each_N, base_path):
    """Generate graphs with different clustering coefficients

    Parameters
    ----------
    N : int
        Size of each graph.
    d : float
        Target density.
    cluster_N : int
        Number of different clustering coefficients.
    each_N : int
        Number of graphs per clustering coefficient.
    base_path : string
        Directory to store graphs.

    """
    sets = []
    clusterings = np.linspace(0.01, 0.99, num=cluster_N)
    for c_i in range(cluster_N):
        c = clusterings[c_i]
        path = "%s_%i" % (base_path, c_i)
        targets = [
            ('components', 1, 1),
            ('density', d, 1),
            ('clustering', c, 1),
        ]
        sets.append((path, targets))

    Generate_multicore(sets, N, each_N)


def Generate_communities(N, d, max_communities, each_N, base_path):
    """Generate graphs with different number of communities

    Parameters
    ----------
    N : int
        Size of each graph.
    d : float
        Target density.
    max_communities : int
        Number of maximum communities
    each_N : int
        Number of graphs per clustering coefficient.
    base_path : string
        Directory to store graphs.

    """
    sets = []
    for i in range(1, max_communities + 1):
        path = "%s_%i" % (base_path, i)
        targets = [
            ('components', 1, 1),
            ('density', d, 1),
            ('modularity', (i, 0.85), 1),
            ('communities', i, 1),
        ]
        sets.append((path, targets))

    Generate_multicore(sets, N, each_N)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--communities', dest='communities',
                        action='store_true',
                        help='Generate graphs for multiple communities')

    parser.add_argument('--clustering', dest='clustering',
                        action='store_true',
                        help='Generate graphs for different clustering coefficients')

    parser.add_argument('--clustering-light', dest='clusteringLight',
                        action='store_true',
                        help='Generate graphs for different clustering coefficients [light version]')

    args = parser.parse_args()

    if args.communities:
        Generate_communities(25, 0.2, 5, 100, "data/communities/communities")

    if args.clustering:
        Generate_clustering(25, 0.2, 100, 100, "data/clustering_lite/clustering")

    if args.clusteringLight:
        Generate_clustering(25, 0.2, 50, 20, "data/clustering_lite/clustering")
