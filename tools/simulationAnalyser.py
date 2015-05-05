#!/usr/bin/env python
import matplotlib.pyplot as plt
import pickle
from deepThought.util import list_to_cdf
from deepThought.stats import Pmf
from deepThought.visualizer.visualizer import visualize
import pylab as pylab
import numpy as np

def main():
    results_ref = pickle.load(open("/tmp/14-11-23--18_1k_ReferenceScheduler-results.pickle", "rb"))
    results_optimized = pickle.load(open("/tmp/14-11-23--18_1k_OptimizedDependencyScheduler-results.pickle", "rb"))
    fig = plt.figure(1)

    ax = plt.subplot(311)


    bins = np.linspace(0, 160000, 60)
    plt.hist(results_ref, bins=bins, normed=0, alpha=0.5, label="reference")
    plt.hist(results_optimized, bins=bins, normed=0, alpha=0.5, label="opt dep")
    plt.legend(loc="upper right")
    ax = plt.subplot(312)
    x_axis, y_axis = list_to_cdf(results_ref)
    ax.plot(x_axis, y_axis, label="ref")
    x_axis, y_axis = list_to_cdf(results_optimized)
    ax.plot(x_axis, y_axis, label="opt dep.")
    plt.legend(loc="lower right")
    plt.xlabel("time in seconds")
    plt.ylabel("cdf")

    ax = plt.subplot(313)
    bp = ax.boxplot([results_ref])
    #pylab.ylim([0,1])
    plt.show()

    #visualize(extremes[0])
    #plt.text(10,32,"Minimum duration of 800 simulations")
    #plt.savefig("/tmp/min.pdf")

    #visualize(extremes[1])
    #plt.text(10,32,"Maximum duration of 800 simulations")
    #plt.savefig("/tmp/max.pdf")


if __name__ == '__main__':
    main()
