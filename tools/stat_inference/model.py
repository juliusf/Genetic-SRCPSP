__author__ = 'jules'

import pymc as mc
import numpy as np

import deepThought.ORM.ORM as ORM

def _model(data):
    #lam1 = mc.Uniform('lam1', 1., upper=10, value=5)
    #p = mc.Uniform('p', 1, 5, value=2)

    #lam2 = mc.Uniform('lam2', 50, upper=200, value=100)

    alpha = mc.Uniform('alpha', lower=0.1, upper=100, value=0.5)
    beta = mc.Uniform('beta', lower=0.1, upper=100, value=1)

    #p = mc.Uniform('p', 0.1, 1, value=0.9)
    #c = mc.Uniform('c', 8, 12, value=10)

    y = mc.Gamma('y', alpha=alpha, beta=beta, value=data, observed=True)
"""
    @mc.stochastic(observed=True)
    def log_hyperexp_like(value=data, lam1=lam1, lam2=lam2, p=p, c=c):
       # return np.log(np.prod(hyperexp2(lam1,lam2,p,value)))
        prod = np.prod(p * lam1 * np.exp(-lam1 * data + c) + (1-p) * lam2 * np.exp(-lam2 * data + c))
        if prod == 0:
            return 0.0
        else:
            return np.log(prod)

"""
