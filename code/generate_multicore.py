"""
    Written by Kārlis Mārtiņš Briedis
"""
import time
import numpy as np
from generate_graph import GraphGenerator
from igraph import Graph
import os
from multiprocessing import Process, cpu_count


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

    for i in range(len(sets)):
        [path, targets] = sets[i]
        os.makedirs(path, exist_ok = True)
        processes = []
        for j in range(each_N):
            fname = "%s/%i.graph" % (path, j)
            proc = Process(target=Generate_single, args=(fname, N, targets))
            processes.append(proc)
            proc.start()

            if len(processes) >= cpu_count() * 3:
                for t in processes:
                    t.join()
                processes = []
                print("Progress: %2.1f%%, %2.1f%%" % ((i+ 1)/len(sets) * 100, (j + 1)/each_N * 100), end='\r')

        for t in processes:
            t.join()

        print("Progress: %2.1f%%" % ((i + 1)/len(sets) * 100), end='\r')

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


if __name__ == "__main__":
    Generate_clustering(25, 0.2, 100, 100, "data/clustering/clustering")
    # Generate_clustering(25, 0.2, 50, 5, "data/clustering_lite/clustering")
