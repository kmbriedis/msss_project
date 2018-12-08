"""
    Written by Kārlis Mārtiņš Briedis
    Based on:
        V. Kashirin, Victor. (2014). Evolutionary Simulation of Complex Networks
            Structures with Specific Topological Properties. Procedia Computer
            Science. 29. 2401-2411. 10.1016/j.procs.2014.05.224.
        Colman, Ewan & Rodgers, Geoff. (2014). Local rewiring rules for evolving
            complex networks. Physica A: Statistical Mechanics and its
            Applications. 416. 80-89. 10.1016/j.physa.2014.08.046.

"""

import igraph
import math
import random

class GraphGenerator():
    """Short summary.

    Parameters
    ----------
    targets : array
        Array of tuples with targets that the graph should approach.
    verbose : Boolean
        Should the progress be printed.

    Attributes
    ----------
    weightsum : float
        Storing weight sum for weight normalization.
    verbose
    targets

    """
    def __init__(self, targets, verbose = True):
        self.verbose = verbose
        self.targets = targets

        self.weightsum = 0
        for i, target in enumerate(self.targets):
            if (len(target) == 2):
                target = (target[0], target[1], 0.5 + random.random())
                self.targets[i] = target

            self.weightsum += target[2]

        # Avoid division by 0
        if self.weightsum == 0:
            self.weightsum = 1

    def evalParameter(self, fn, g, target):
        """Evaluates given parameter and the matching score

        Parameters
        ----------
        fn : string
            Name of parameter.
        g : igraph.Graph
            Graph which parameter is evaluated.
        target : mixed
            Target value for given parameter.

        Returns
        -------
        tuple
            0 - float[0;1] - matching score (1 - parameter meets target)
            1 - float - evaluated parameter

        """
        map_fn = 'l_scale'
        value = 0

        if fn == 'density':
            value = g.density()
            map_fn = 's_scale'
        elif fn == 'clustering':
            clust = g.transitivity_avglocal_undirected()
            if  math.isnan(clust):
                return 0, 0
            value = clust
            map_fn = 's_scale'
        elif fn == 'apl': #average path length
            value = g.average_path_length()
            if  math.isnan(value):
                return 0, 0
        elif fn == 'components':
            value = len(g.components())
        elif fn == 'communities':
            if (len(g.components()) > 1):
                return 0, 0
            g.simplify()
            value = g.community_fastgreedy().optimal_count
        elif fn == 'modularity':
            if (len(g.components()) > 1):
                return 0, 0
            g.simplify()
            communities = g.community_fastgreedy().as_clustering(target[0])
            value = communities.modularity
            target = target[1]
            map_fn = 's_scale'
        else:
            raise ValueError('Invalid target "%s"' % (fn))

        if map_fn == 'l_scale':
            return 1 / (abs(target - value) + 1), value
        else:
            return 1 - abs(target - value), value

    def graph_energy(self, g):
        """Calcualtes energy of given graph

        Parameters
        ----------
        g : igraph.Graph
            Graph to evaluate

        Returns
        -------
        float[0;1]
            Graph energy where 0 means that graph matches all target parameters

        """
        psi = 0

        for target in self.targets:
            psi += target[2] * self.evalParameter(target[0], g, target[1])[0]

        return 1 - psi / self.weightsum;

    def print(self, g):
        """Prints graph's matching to given target parameters

        Parameters
        ----------
        g : igraph.Graph

        """
        for target in self.targets:
            value = self.evalParameter(target[0], g, target[1])
            if isinstance(target[1], tuple):
                target = (target[0], target[1][1], target[2])
            print("%s %f/%f" % (target[0], value[1], target[1]))

    def mutate(self, g, count = 5, local = None):
        """Perform n random mutations on the graph
           Mutations [0, 1, 2, 3] based on Kashirin (2014)
           Mutation [4] based on Colman & Rodgers (2014)

        Parameters
        ----------
        g : igraph.Graph
            Graph to mutate
        count : int
            Number of mutations.
        local : Boolean
            Whether to perform a local or global modification.

        """
        if local is None:
            local = random.random() > 0.5

        if local:
            modifications = [0, 3, 4]
        else:
            modifications = [0, 1, 2]

        N = g.vcount()

        for _ in range(count):
            [s] = random.sample(modifications, 1)

            adjl = g.get_adjlist()
            with_neighbors = [(i, a) for i, a in enumerate(adjl) if len(a) > 0]
            neighbors_c = [len(a) for a in adjl]
            min_n = min(neighbors_c)
            max_n = max(neighbors_c)

            if s == 0:
                # removes random edge
                if max_n > 0:
                    [node] = random.sample(with_neighbors, 1)
                    [j] = random.sample(node[1], 1)
                    g.delete_edges([(node[0],j)])
            elif s == 1:
                # adds random edge
                i, j = random.sample(range(N), 2)
                if not g.are_connected(i, j):
                    g.add_edge(i, j)
            elif s == 2:
                # Global rewire
                # choosing 4 vertices so that there are
                # only edges i->j and m->n
                # and transforming them to edges m->j and i->n
                if len(with_neighbors) > 2:
                    max_tries = len(with_neighbors) ** 2
                    i, m = random.sample(with_neighbors, 2)
                    [j] = random.sample(i[1], 1)
                    i = i[0]
                    [n] = random.sample(m[1], 1)
                    m = m[0]
                    while max_tries > 0 and (g.are_connected(i, m) or g.are_connected(i, n) or g.are_connected(j, m) or g.are_connected(j, n)):
                        i, m = random.sample(with_neighbors, 2)
                        [j] = random.sample(i[1], 1)
                        i = i[0]
                        [n] = random.sample(m[1], 1)
                        m = m[0]
                        max_tries -= 1
                    if max_tries > 0:
                        g.delete_edges([(i,j), (m, n)])
                        g.add_edge(m, j)
                        g.add_edge(i, n)
            elif s == 3:
                # Connecting local nodes
                # Making connection between random vertex i
                # and j, so that distance d between i and j is 1<d<5
                if len(with_neighbors) > 1:
                    [node] = random.sample(with_neighbors, 1)
                    forder = set(node[1])
                    lookup = set(node[1])
                    for _ in range(3):
                        for v in lookup.copy():
                            lookup.update(adjl[v])
                    local = lookup.difference(forder)
                    if len(local) > 1:
                        [j] = random.sample(local, 1)
                        g.add_edge(node[0], j)
            elif s == 4:
                # Local rewiring
                # Choosing 3 vertices with only 2 edges
                # and adding the missing edge but deleting one
                # of initial edges
                if max_n > 2:
                    max_tries = len(with_neighbors) ** 2
                    while max_tries > 0:
                        max_tries -= 1
                        [i] = random.sample(with_neighbors, 1)

                        if len(i[1]) > 2:
                            [j, k] = random.sample(i[1], 2)

                            if not g.are_connected(j, k):
                                break

                    if max_tries > 0:
                        g.delete_edges([(i[0],j)])
                        g.add_edge(j, k)

    def update_temperature(self, T0, t, r):
        """Updates simulated annealing temperature for next iteration

        Parameters
        ----------
        T0 : float
            Initial temperature.
        t : int
            Iteration.
        r : float
            Cooling rate.

        Returns
        -------
        float
            Temperature for iteration t.

        """
        return T0 / (1 + r * t)

    def simulated_annealing(self, g, T0 = 0.03, r = 0.001, max_iter = 100000):
        """Simulated annealing approach for graph generation.

        Parameters
        ----------
        g : igraph.Graph
            Initial graph.
        T0 : float
            Initial temperature.
        r : float
            Cooling rate.
        max_iter : type
            Maximum amount of iterations.

        Returns
        -------
        tuple
            0 - graph with minimized energy
            1 - energy of this graph

        """
        print_step = int(max_iter / 1000)
        next_print = 0
        T = T0
        t = 0

        min_t =  self.update_temperature(T0, max_iter, r)

        E_best = 100
        best_g = g

        E_cur = 1
        while T > min_t and E_cur > 1e-6:
            E_cur = self.graph_energy(g)
            g_new = g.copy()
            self.mutate(g_new, count = 3) #, local = t/max_iter > random.random())
            E_new = self.graph_energy(g_new)
            if (math.exp(-1/T * max(0, E_new - E_cur))) > random.random():
                g = g_new

            if E_new < E_best:
                E_best = E_new
                best_g = g_new.copy()

            T = self.update_temperature(T0, t, r)
            t += 1

            if next_print == 0:
                next_print = print_step
                if self.verbose:
                    print("Temp: %.3f, progress: %2.1f%%, energy: %f" % (T, t/max_iter * 100, E_cur), end='\r')
            next_print -= 1

        if self.verbose:
            print("\r\n")
        return best_g, self.graph_energy(best_g)


    def local_minima(self, g, iter = 2000):
        """ Additional graph generation approach that
            always chooses the graph with minimum energy

        Parameters
        ----------
        g : Graph
        iter : int
            Number of iterations.

        Returns
        -------
        tuple
            0 - graph with minimized energy
            1 - energy of this graph

        """
        print_step = int(iter / 1000)
        next_print = 0

        best_g = g
        best_e = 1
        for i in range(iter):
            best_iter_g = None
            best_iter_e = 1
            for _ in range(50):
                g_new = best_g.copy()
                self.mutate(g_new, count = 3, local = i/iter > random.random())
                e = self.graph_energy(g_new)
                if (e < best_iter_e):
                    best_iter_e = e
                    best_iter_g = g_new
            if best_iter_e < best_e or True:
                best_g = best_iter_g
                best_e = best_iter_e

            if next_print == 0:
                next_print = print_step
                print("Progress: %2.1f%%, energy: %f" % (i/iter * 100, best_e), end='\r')
            next_print -= 1
        return best_g, best_e


def Make_directed(g):
    """As the result of graph generation is undirected
       graph, this function randomly chooses direction of ever edge.

    Parameters
    ----------
    g : igraph.Graph
        Undirected graph

    Returns
    -------
    igraph.Graph
        Directed graph

    """

    g = g.as_directed()

    N = g.vcount()
    edges = [(i, edge) for i, edge in enumerate(g.get_edgelist())]
    random.shuffle(edges)
    existing = [[False for _ in range(N)] for _ in range(N)]
    to_delete = []

    for i, edge in edges:
        if existing[edge[0]][edge[1]]:
            to_delete.append(i)
        else:
            existing[edge[0]][edge[1]] = existing[edge[1]][edge[0]] = True

    g.delete_edges(to_delete)

    return g


if __name__ == "__main__":

    G = igraph.Graph(25)

    targets = [
        ('components', 1, 1),
        ('clustering', 0.52, 1),
        ('apl', 3.55, 1)
    ]

    gen = GraphGenerator(targets)

    [g, energy] = gen.simulated_annealing(G)
    g.write_pickle("graph")
    gen.print(g)
