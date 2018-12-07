from generate_graph import Random_graph, Make_directed
import numpy as np
import random
import matplotlib.pyplot as plt
import random_graph

def apply(g, E, gamma, theta):
    """ Generating weights for given topology
        Reference to paper?

    Parameters
    ----------
    g : igraph.Graph
        Given graph.
    E : float
        Total external assets of network.
    gamma : float
        Net worth as percenage of total assets.
    theta : float
        Interbank assets as percenage of total assets.

    Returns
    -------
    6xN array [a, e, i, c, d, b]
        a - individual bank's assets
        e - external assets
        i - interbank assets
        c - net worths
        d - customers' deposits
        b - interbank borrowing

    """

    N = g.vcount()
    beta = 1 - theta
    A = E / beta;
    I = theta * A
    Z = g.ecount()

    w = I / Z
    M = np.array(g.get_adjacency().data)

    i_full = M * w

    i = w * np.sum(M, 1)
    b = w * np.sum(M.transpose(), 1)

    # e_tilde = np.maximum(b - i, np.zeros(i.size))
    e_tilde = b - i

    E_left = E  - sum(e_tilde)
    e = e_tilde + E_left / N

    a = e + i
    c = gamma * a
    d = a - c - b

    return a, e, i, c, d, b, i_full, w


def simulate(g, weights, shock_size, shock_bank):
    [a, e, i, c, d, b, i_full, _] = weights
    i_full = np.array(i_full)
    b = np.array(b)
    c = np.array(c)
    N = g.vcount()

    not_defaulted = np.ones(N, dtype=int)
    shock = np.zeros(N)

    shock[shock_bank] = min(shock_size, a[shock_bank])

    eps = 1
    while max(shock) > eps and max(c) > eps:
        for s_i in range(N):
            s_shock = shock[s_i]
            if s_shock > eps:
                not_absorbed = max(0, s_shock - c[s_i])
                c[s_i] = max(0, c[s_i] - s_shock)
                shock[s_i] = 0

                # calculate only interbank
                not_absorbed = min(not_absorbed, b[s_i])
                if not_absorbed > 0:
                    b[s_i] -= not_absorbed

                    # i_full is used in case we modify
                    # the distribution that all weights are not equal
                    borrowers = i_full[:, s_i]
                    borrowed = sum(borrowers)
                    loss = borrowers * not_absorbed / borrowed
                    i_full[:, s_i] = i_full[:, s_i] - loss
                    shock = shock + loss
                    not_defaulted[s_i] = 0

            shock[s_i] = 0

    return sum([1 if x < eps else 0 for x in c])


def sim_defaults(E, N, p, theta, gamma, shock):
    G = random_graph.Directed2(N, p)
    # G = Random_graph(N, p * 2)
    # G = Make_directed(G)
    weights = apply(G, E, gamma, theta)
    defaults = []
    for bank in range(G.vcount()):
        defaults.append(simulate(G, weights, shock, bank))

    return sum(defaults) / G.vcount()


def plot_results(x, results):
    results = np.array(results)

    # Plot results
    mu = np.mean(results, 1)
    std = np.std(results, 1)

    fig, ax = plt.subplots(1)
    ax.plot(x, mu, lw=2, label='', color='blue')
    ax.fill_between(x, np.max(results, 1), np.min(results, 1), facecolor='blue', alpha=0.5)
    # ax.legend(loc='upper left')
    ax.set_xlabel('Variable')

    ticks = ax.get_xticks()
    ax.set_xticklabels(["%.2f%%" % (x * 100) for x in ticks])
    np.mean(results, 1)
    ax.set_ylabel('Number of defaults')
    ax.grid()
    plt.show()


def gamma_variation():
    gammas = np.linspace(0, 0.1, num=100)

    results = [[] for _ in gammas]

    for i, gamma in enumerate(gammas):
        print(i, end='\r')
        for _ in range(100):
            results[i].append(sim_defaults(100000, 25, 0.2, 0.2, gamma, 100000))

    plot_results(gammas, results)


def p_variation():
    probs = np.linspace(0.01, 0.99, num=100)

    results = [[] for _ in probs]

    for i, p in enumerate(probs):
        print(i, end='\r')
        for _ in range(20):
            results[i].append(sim_defaults(100000, 25, p, 0.2, 0.01, 100000))

    plot_results(probs, results)


if __name__ == "__main__":
    gamma_variation()
    # p_variation()
    # print(sim_defaults(100000, 25, 0.2, 0.2, 0.2, 100000))
