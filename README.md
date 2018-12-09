# Modeling and Simulation of Social Systems Fall 2018 – Research Plan (Template)

(text between brackets to be removed)

> * Group Name: TBD
> * Group participants names: Bachiri Anas, Briedis Karlis Martins
> * Project Title: Financal Networks & Cirsis
> * Programming language: Python

## General Introduction

(States your motivation clearly: why is it important / interesting to solve this problem?)
(Add real-world examples, if any)
(Put the problem into a historical context, from what does it originate? Are there already some proposed solutions?)

## The Model

(Define dependent and independent variables you want to study. Say how you want to measure them.) (Why is your model a good abstraction of the problem you want to study?) (Are you capturing all the relevant aspects of the problem?)

## Fundamental Questions

(At the end of the project you want to find the answer to these questions)
(Formulate a few, clear questions. Articulate them in sub-questions, from the more general to the more specific. )

## Expected Results

(What are the answers to the above questions that you expect to find before starting your research?)

## References

Nier, Erlend & Yang, Jing & Yorulmazer, Tanju & Alentorn, Amadeo. (2008). Network Models and Financial Stability. Journal of Economic Dynamics and Control. 31. 2033-2060. 10.1016/j.jedc.2007.01.014.

(Add the bibliographic references you intend to use)
(Explain possible extension to the above models)
(Code / Projects Reports of the previous year)

## Research Methods

(Cellular Automata, Agent-Based Model, Continuous Modeling...) (If you are not sure here: 1. Consult your colleagues, 2. ask the teachers, 3. remember that you can change it afterwards)

## Other

(mention datasets you are going to use)

# Reproducibility

> Prerequisite for all reproducibility tests is `python >=3.6`

### Installing dependencies

```
python -m pip install numpy matplotlib python-igraph
```

> For installation of igraph, please refer to its [python-igraph Manual](https://igraph.org/python/doc/tutorial/install.html).
> **_For Windows users_** a convinient way is to use [unofficial windows binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-igraph) by downloading suitable `.whl` file and running e.g. `pip install python_igraph‑0.7.1.post6‑cp36‑cp36m‑win_amd64.whl`

### Cloning the project

```
git clone git@github.com:kmbriedis/msss_project.git
cd msss_project/code
```

## Light test

To run light tests, make sure all dependencies are installed and you are in cloned directory.

### Reproducing default dynamics

To reproduce results of Nier et al., (...) run (running time 1-2 minutes):

```
python test_light.py --reproduce-sim
```

|                                       | Light test                                                   | Full test                                                  | Nier et al.                                                       |
| ------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| Percentage net worth variation        | ![Net worth variation - light](media/gamma_light.png)        | ![Net worth variation - full](media/gamma_full.png)        | ![Net worth variation - Nier et al.](media/gamma_Nier.png)        |
| Percentage interbank assets variation | ![Interbank assets variation - light](media/theta_light.png) | ![Interbank assets variation - full](media/theta_full.png) | ![Interbank assets variation - Nier et al.](media/theta_Nier.png) |
| Erdös-Rényi probability variation     | ![Density variation - light](media/density_light.png)        | ![Density variation - full](media/density_full.png)        | ![Density variation - Nier et al.](media/density_Nier.png)        |

(step by step instructions to reproduce your results. _Keep in mind that people reading this should accomplish to reproduce your work within 10 minutes. It needs to be self-contained and easy to use_. e.g. git clone URL_PROY; cd URL_PROY; python3 main.py --light_test (#--light test runs in less than 5minutes with up to date hardware))

### Reproducing default dynamics on graphs with specific topological properties

There are pregenerated graphs in `other/pregenerated_graphs` directory. Unzip `clustering_light.zip` and `communities.zip` in your chosen **`$UNZIP_DIR`**

Run:

```
python test_light.py --sim-communities $UNZIP_DIR/communities
python test_light.py --sim-clustering $UNZIP_DIR/clustering_light
```

### BONUS: Reproducing complex network structure generation

TODO

## Full test
