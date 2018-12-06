from generate_graph import Random_graph, Make_directed
import numpy as np
import random
import matplotlib.pyplot as plt
from random_graph import Directed as Random_directed

def apply(g, E, gamma, theta):
    N = g.vcount()
    beta = 1 - theta
    A = E / beta;
    I = theta * A
    Z = g.ecount()

    w = I / Z
    M = np.array(g.get_adjacency().data)

    i = w * np.sum(M, 1)
    b = w * np.sum(M.transpose(), 1)

    e_tilde = np.maximum(b - i, np.zeros(i.size))
    E_left = E - sum(e_tilde)
    e = e_tilde + E_left / N

    a = e + i
    c = gamma * a
    d = a - c - b

    return a, e, i, c, d, b


def simulate(g, weights, shock_size, shock_bank):
    [a, e, i, c, d, b] = weights
    N = g.vcount()
    M = np.array(g.get_adjacency().data)

    not_defaulted = np.ones(N, dtype=int)
    shock = np.zeros(N)

    shock[shock_bank] = shock_size

    while sum(shock) > 0 and sum(not_defaulted) > 0:
        c -= shock
        shock = np.zeros(N)

        defaulted_in_step = not_defaulted * np.less(c, 0)

        for i, rl in enumerate(defaulted_in_step * c):
            if rl < 0:
                creditors = not_defaulted * M[:,i]
                creditor_count = sum(creditors)

                if creditor_count > 0:
                    shock += (abs(rl) / creditor_count) * creditors

                not_defaulted[i] = False

    return N - sum(not_defaulted)


def sim_defaults(E, N, p, theta, gamma, shock):
    G = Random_directed(N, p)
    weights = apply(G, E, gamma, theta)
    defaults = simulate(G, weights, shock, random.randint(0, G.vcount() - 1))
    return defaults


def gamma_variation():
    gammas = np.linspace(0, 0.1, num=41)

    results = [[] for _ in gammas]

    for i, gamma in enumerate(gammas):
        print(i, end='\r')
        for _ in range(100):
            results[i].append(sim_defaults(100000, 25, 0.2, 0.2, gamma, 4000))

    results = np.array(results)


    # Plot results
    mu = np.mean(results, 1)
    std = np.std(results, 1)

    fig, ax = plt.subplots(1)
    ax.plot(gammas, mu, lw=2, label='', color='blue')
    ax.fill_between(gammas, mu + std, mu - std, facecolor='blue', alpha=0.5)
    # ax.legend(loc='upper left')
    ax.set_xlabel('Percenage net worth')

    ticks = ax.get_xticks()
    ax.set_xticklabels(["%.2f%%" % (x * 100) for x in ticks])
    np.mean(results, 1)
    ax.set_ylabel('Number of defaults')
    ax.grid()
    plt.show()


if __name__ == "__main__":
    gamma_variation()
