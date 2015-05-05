__author__ = 'jules'

import deepThought.ORM.ORM as ORM

import pymc
import gamma_model
import numpy as np
from numpy import mean
from scipy.stats import gamma
import matplotlib.pylab as plt

def main():


    model=pymc.MCMC(gamma_model)
    model.sample(iter=1000, burn=500, thin=2)

    alpha = mean(model.trace('alpha')[:])
    beta = mean(model.trace('beta')[:])
    print('alpha: %s' % alpha)
    print('beta: %s' % beta )

    x = np.linspace(0, 100, 0.001)
    y = gamma.pdf(x, alpha, scale= 1.0 / beta)

    plt.plot(x,y)
    plt.xlim([0,100])
    plt.ylim([0,0.001])
    plt.show()


if __name__=='__main__':
    main()