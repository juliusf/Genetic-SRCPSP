__author__ = 'jules'

import deepThought.ORM.ORM as ORM
import matplotlib.pyplot as plt
import numpy as np


def main():
    job = ORM.deserialize("/tmp/output.pickle")

    results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

    set1 = results[0].execution_history
    set2 = results[1].execution_history

    shape = 0.65700176667
    scale= 9835.05623957

    x = np.array(set2)
    rank = np.arange(1,x.size+1)  # ranks = {1, 2, 3, ... 10}
    median_rank = (rank - 0.3)/(rank.size + 0.4)
    y = np.log(-np.log(1 - median_rank))

    # Generate 1000 numbers following a Weibull distribution that we think ideally fits our data using the shape and scale parameter
    x_ideal = scale *np.random.weibull(shape, size=100)
    x_ideal.sort()
    F = 1 - np.exp( -(x_ideal/scale)**shape )
    y_ideal = np.log(-np.log(1 - F))

    # Weibull plot
    fig1 = plt.figure()
    fig1.set_size_inches(11,9)
    ax = plt.subplot(111)
    plt.semilogx(x, y, "bs")
    plt.plot(x_ideal, y_ideal, 'r-', label="beta= %5G\neta = %.5G" % (shape, scale) )
    plt.title("Weibull Probability Plot on Log Scale", weight="bold")
    plt.xlabel('x (time)', weight="bold")
    plt.ylabel('Cumulative Distribution Function', weight="bold")
    plt.legend(loc='lower right')

    # Generate ticks
    def weibull_CDF(y, pos):
        return "%G %%" % (100*(1-np.exp(-np.exp(y))))

    formatter = plt.FuncFormatter(weibull_CDF)
    ax.yaxis.set_major_formatter(formatter)

    yt_F = np.array([ 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5,
               0.6, 0.7, 0.8, 0.9, 0.95, 0.99])
    yt_lnF = np.log( -np.log(1-yt_F))
    plt.yticks(yt_lnF)
    ax.yaxis.grid()
    ax.xaxis.grid(which='both')
    plt.show()
    """
    ax = plt.subplot(311)


    bins = np.linspace(0, 8000, 20)
    plt.hist(set1, bins=bins, normed=0, alpha=0.5, label="reference")
    plt.hist(set2, bins=bins, normed=0, alpha=0.5, label="opt dep")
    plt.legend(loc="upper right")

    plt.show()
    """

if __name__ == '__main__':
    main()
