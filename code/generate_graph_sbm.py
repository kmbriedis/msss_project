#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 17:53:21 2018

@author: bachiri
"""
import numpy as np
import igraph

def GenerateNetworkSBM(sbm, z):
    # Generate empty network    
    network = igraph.Graph(n=len(z), directed = True)

    # Draw links randomly according to stochastic block matrix
    for u in network.vs():
        for v in network.vs():
            if (u.index < v.index):
                if np.random.random() <= sbm[z[u.index], z[v.index]]:
                    network.add_edge(u, v)
    return network