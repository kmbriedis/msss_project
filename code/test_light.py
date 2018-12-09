"""
    Written by Kārlis Mārtiņš Briedis
"""
import argparse
import numpy as np
import time
import matplotlib.pyplot as plt

from simulation import Multicore_variation, plot_results, plot_results_multiple
from eval_pregenerated import Evaluate_pregenerated

DEFAULT_PARAMS = {
    'E': 100000,
    'N': 25,
    'gamma': 0.05,
    'density': 0.2,
    'theta': 0.2,
    'shock': 100000,
}


def gamma_variation():
    print("Variating net worth")
    gammas = np.linspace(0, 0.1, num=50)

    variables = []
    for gamma in gammas:
        params = (DEFAULT_PARAMS['E'], DEFAULT_PARAMS['N'],
                  DEFAULT_PARAMS['density'], DEFAULT_PARAMS['theta'],
                  gamma, DEFAULT_PARAMS['shock'])
        variables.append(params)

    results = Multicore_variation(variables, 20)

    plot_results(gammas, "Percentage net worth", DEFAULT_PARAMS['N'], results)


def theta_variation():
    print("Variating interbank assets")
    thetas = np.linspace(0, 0.5, num=50)

    variables = []
    for theta in thetas:
        params = (DEFAULT_PARAMS['E'], DEFAULT_PARAMS['N'],
                  DEFAULT_PARAMS['density'], theta,
                  DEFAULT_PARAMS['gamma'], DEFAULT_PARAMS['shock'])
        variables.append(params)

    results = Multicore_variation(variables, 20)

    plot_results(thetas, "Percentage interbank assets", DEFAULT_PARAMS['N'], results)


def p_variation():
    print("Variating density")
    probs = np.linspace(0.01, 0.99, num=50)

    results = []
    labels = []
    for gamma in [0.01, 0.03, 0.07]:
        print("Gamma %.2f" % gamma)
        variables = []
        for p in probs:
            params = (DEFAULT_PARAMS['E'], DEFAULT_PARAMS['N'],
                      p, DEFAULT_PARAMS['theta'],
                      gamma, DEFAULT_PARAMS['shock'])
            variables.append(params)
        results.append(Multicore_variation(variables, 20))
        labels.append("Net worth %.0f%%" % (gamma * 100))

    plot_results_multiple(probs, "Erdös-Rényi probability", DEFAULT_PARAMS['N'], results, labels)


def reproduceSim():
    start_time = time.time()
    gamma_variation()
    theta_variation()
    p_variation()
    print("Took %i seconds" % (time.time() - start_time))
    plt.show()


def simCommunities(base_path):
    start_time = time.time()
    print("Variating communities on pregenerated graphs")

    results = []
    labels = []
    evalParam = lambda g, _: g.community_fastgreedy().optimal_count
    for gamma in [0.005, 0.01, 0.05]:
        print("Gamma %.2f" % gamma)
        simParams = (DEFAULT_PARAMS['E'], gamma, DEFAULT_PARAMS['theta'], DEFAULT_PARAMS['E'])
        params, defaults, N = Evaluate_pregenerated(base_path, evalParam, simParams)
        results.append(defaults)
        labels.append("Net worth %.1f%%" % (gamma * 100))

    plot_results_multiple(params, "Number of communities", N, results, labels)
    print("Took %i seconds to complete    " % (time.time() - start_time))
    plt.show()


def simClustering(base_path):
    start_time = time.time()
    print("Variating clustering on pregenerated graphs")

    results = []
    labels = []
    evalParam = lambda _, g: g.transitivity_avglocal_undirected()
    for gamma in [0.005, 0.01, 0.05]:
        print("Gamma %.2f" % gamma)
        simParams = (DEFAULT_PARAMS['E'], gamma, DEFAULT_PARAMS['theta'], DEFAULT_PARAMS['E'])
        params, defaults, N = Evaluate_pregenerated(base_path, evalParam, simParams)
        results.append(defaults)
        labels.append("Net worth %.1f%%" % (gamma * 100))

    plot_results_multiple(params, "Clustering coefficient", N, results, labels)
    print("Took %i seconds to complete    " % (time.time() - start_time))
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--reproduce-sim', dest='reproduceSim',
                        action='store_true',
                        help='Reproduce crisis simulation methods described in paper "Network models and financial stability"')

    parser.add_argument('--sim-communities', dest='simCommunities', default=False)

    parser.add_argument('--sim-clustering', dest='simClustering', default=False)

    args = parser.parse_args()

    if args.reproduceSim:
        reproduceSim()
    elif args.simCommunities:
        simCommunities(args.simCommunities)
    elif args.simClustering:
        simClustering(args.simClustering)
    else:
        print("No action selected")
