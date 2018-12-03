import igraph
import math
import random

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


class GraphGenerator():
    def __init__(self, targets, weights = {}):
        default_weights = {
            'density': 1,
            'degree': 1,
            'clustering': 1,
        }

        weights = {**default_weights, **weights}

        self.targets = targets
        self.weights = weights

        self.weightsum = 0
        for x in weights:
            self.weightsum += weights[x]

        # Avoid division by 0
        if self.weightsum == 0:
            self.weightsum = 1

    def graph_energy(self, g):
        psi = 0
        psi = psi + self.weights['degree'] * (1 / (1 + abs(self.targets['degree'] - mean(g.degree()))))
        psi = psi + self.weights['density'] * (1 - abs(g.density() - self.targets['density']))

        clust = g.transitivity_avglocal_undirected()
        if not math.isnan(clust):
            psi = psi + self.weights['clustering']  * (1 - abs(clust - self.targets['clustering']))

        return 1 - psi / self.weightsum;

    def mutate(self, g, count = 5):
        for _ in range(count):
            s = random.randint(0, 3)
            adjl = g.get_adjlist()
            with_neighbors = [(i, a) for i, a in enumerate(adjl) if len(a) > 0]
            neighbors_c = [len(a) for a in adjl]
            min_n = min(neighbors_c)
            max_n = max(neighbors_c)
            if s == 0: # remove edge
                if max_n > 0:
                    [node] = random.sample(with_neighbors, 1)
                    [j] = random.sample(node[1], 1)
                    g.delete_edges([(node[0],j)])
            elif s == 1: # add edge
                if min_n < g.vcount() - 1:
                    max_tries = len(with_neighbors) ** 2
                    i, j = random.sample(range(g.vcount()), 2)
                    while max_tries > 0 and g.are_connected(i, j):
                        i, j = random.sample(range(g.vcount()), 2)
                        max_tries -= 1
                    g.add_edge(i, j)
            elif s == 2: # rewiring
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
            elif s == 3: # connect local
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

    def update_temperature(self, T0, t, r):
        return T0 / (1 + r * t)

    def simulated_annealing(self, g, T0 = 0.03, r = 0.001, max_iter = 10000):

        T = T0
        t = 0

        min_t =  self.update_temperature(T0, max_iter, r)

        E_best = 100
        best_g = g

        E_cur = 1
        while T > min_t and E_cur > 1e-4:
            E_cur = self.graph_energy(g)
            g_new = g.copy()
            self.mutate(g_new)
            E_new = self.graph_energy(g_new)
            if (math.exp(-1/T * max(0, E_new - E_cur))) > random.random():
                g = g_new

            if E_new < E_best:
                E_best = E_new
                best_g = g_new.copy()

            T = self.update_temperature(T0, t, r)
            t += 1

            print("Temp: %.3f, progress: %2.1f%%, energy: %f" % (T, t/max_iter * 100, E_cur), end='\r')

        print("\r\n")
        return best_g, self.graph_energy(g)




def Erdos_Renyi(n, p):
    return igraph.Graph.Erdos_Renyi(n, p, directed=False, loops=False)


if __name__ == "__main__":

    N = 504
    targets = {
        'density': 0.062,
        'degree': 15.61,
        'clustering': 0.087,
    }

    weights = {
        'density': 1,
        'degree': 0.1,
        'clustering': 1,
    }

    G = Erdos_Renyi(500, 0)

    gen = GraphGenerator(targets, weights)

    [g, energy] = gen.simulated_annealing(G)

    print(g.density())
    print(mean(g.degree()))
    print(g.transitivity_avglocal_undirected())
