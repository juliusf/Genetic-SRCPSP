__author__ = 'jules'

import numpy as np
import deepThought.ORM.ORM as ORM
from scipy.optimize import fmin
from deepThought.stats.Pmf import MakePmfFromList
from deepThought.util import list_to_ccdf
import matplotlib.pyplot as plt
import pylab as pylab

def main():
    job = ORM.deserialize("/tmp/output.pickle")

    results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

    set1 = results[0].execution_history
    data = np.array(set1)
    data
    def to_fit(params):
        lam1 = params[0]
        lam2 = params[1]
        p = params[2]
        c = params [3]
        return - log_hyperexp_like(lam1, lam2, p, c, data)

    pmf = MakePmfFromList(set1)
    x,y = pmf.Render()
    initParams = [10 ** -4, 10 ** 2, 0.9, 10]
    results = fmin(to_fit, initParams, maxiter=10000000)
    print(results)

    x = np.arange(0, 1000, 0.1)
    s = hyperexp2(results[0], results[1], results[2], results[3], x)
    x,y = list_to_ccdf(s.tolist())
    pylab.xlim([0,1000])
    pylab.ylim([0,0.0006])
    plt.plot(x,y)
    #pylab.xlim([0,90000])
    #pylab.ylim([0,1])
    plt.show()
    print results





def hyperexp2(lambda1, lambda2, p, c ,x ):
        return  p * lambda1 * np.exp(-lambda1 * x + c) + (1-p) * lambda2 * np.exp(-lambda2 * x + c)

def log_hyperexp_like(x, lam1, lam2, c, p):
        prod = np.prod(p * lam1 * np.exp(-lam1 * x + c) + (1-p) * lam2 * np.exp(-lam2 * x + c))
        if prod == 0:
            return 0.0
        else:
            return np.log(prod)

def exp_like(x, lam):
    n = len(x)
    return n*np.ln(lam) - lam * np.sum(x)

def exponential_pdf(lam, x):
        return lam * np.exp(-lam*x)


if __name__=='__main__':
    main()