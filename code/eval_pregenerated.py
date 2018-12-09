"""
    Written by Kārlis Mārtiņš Briedis
"""
import simulation
import os
from igraph import Graph
import multiprocessing
import time
import numpy as np
from generate_graph import Make_directed
import matplotlib.pyplot as plt


def Simulate_single(g, simParams):

    if len(simParams) == 3:
        [E, gamma, theta] = simParams
        shock_size = E
    else:
        [E, gamma, theta, shock_size] = simParams

    N = g.vcount()

    weights = simulation.apply(g, E, gamma, theta)
    defaults = 0
    for bank in range(N):
        defaults += simulation.simulate(g, weights, shock_size, bank)

    return defaults / N


def Evaluate_pregenerated(base_path, evalParam, simParams):
    groups = []
    graphs = []
    N = 0
    print("Loading graphs...")

    for dirpath, dirnames, filenames in os.walk(base_path):
        if len(filenames) < 1:
            continue

        if dirpath in groups:
            group = groups.index(dirpath)
        else:
            group = len(groups)
            groups.append(dirpath)

        for filename in [f for f in filenames if f.endswith(".graph")]:
            path = os.path.join(dirpath, filename)
            undirected_g = Graph.Read_Pickle(path)
            directed_g = Make_directed(undirected_g)
            N = max(directed_g.vcount(), N)
            param = evalParam(undirected_g, directed_g)
            graphs.append((directed_g, group, param))

    if len(graphs) < 1:
        print("No graphs found")
        return [], []

    print("Loaded %i graphs" % len(graphs))
    print("Launching tasks...")

    pool = multiprocessing.Pool()
    rs = pool.starmap_async(Simulate_single, [(x[0], simParams) for x in graphs])

    pool.close()

    while (True):
      if (rs.ready()): break
      remaining = rs._number_left
      print("Waiting for %i tasks to complete..." % (remaining), end="\r")
      time.sleep(1)

    defaults = rs.get()

    defaults_per_group = [[] for _ in range(len(groups))]
    values_per_group = [[0, 0] for _ in range(len(groups))]
    for i, info in enumerate(graphs):
        defaults_per_group[info[1]].append(defaults[i])
        values_per_group[info[1]].append(info[2])


    mean_values = np.mean(values_per_group, 1)
    sorted_defaults = [x for _,x in sorted(zip(mean_values,defaults_per_group))]
    mean_values.sort()

    return mean_values, sorted_defaults, N
