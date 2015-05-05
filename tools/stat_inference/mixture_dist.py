
__author__ = 'jules'
#see http://nbviewer.ipython.org/github/timstaley/ipython-notebooks/blob/compiled/probabilistic_programming/convolving_distributions_illustration.ipynb

import deepThought.ORM.ORM as ORM
from deepThought.util import list_to_cdf

from deepThought.stats.phase_type import infer_distribution
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from deepThought.stats.customDistributions import MixtureDist2


def main():

    job = ORM.deserialize("/tmp/output.pickle")

    results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

    jobs = []
    for x in results:
        mean = np.mean(x.execution_history)
        cx = np.sqrt(np.var(x.execution_history)) / mean
        if cx >= 1:
            jobs.append(x)

    #set1 = jobs[1].execution_history
    set1 = results[1].execution_history
    data = np.array(set1)
    mean = np.mean(data)
    var = np.var(data)
    dist = infer_distribution(data)
    errscale = 10
    err = stats.norm(loc=mean , scale=var)

    delta = 1


    sum_rv_delta_size = 1e2#1e-2
    mixt = MixtureDist2(0.1, err, dist)
    data_x, data_y = list_to_cdf(set1)
    new_grid = np.arange(0,90000, 100)
    plt.plot(new_grid, dist.cdf(new_grid), label='uniform')
    plt.plot(new_grid, err.cdf(new_grid), label='gaussian')
    plt.plot(new_grid, mixt.cdf(new_grid), label='Sum')
    plt.plot(data_x, data_y, label="data")
    #plt.xlim(0,max(new_grid))
    plt.legend(loc='best'), plt.suptitle('CDFs')
    #plt.ylim(-0.1,1.1)

    plt.show()

if __name__ == '__main__':
    main()