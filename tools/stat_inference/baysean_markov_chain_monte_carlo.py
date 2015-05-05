__author__ = 'jules'

import pymc as mc
from model import _model
import numpy as np
import pylab
import deepThought.ORM.ORM as ORM
from deepThought.util import list_to_ccdf
from numpy import mean
import matplotlib.pyplot as plt
import pylab as pylab

def main():
    job = ORM.deserialize("/tmp/output.pickle")

    results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

    set1 = results[0].execution_history

    f = open('/tmp/data.table','w')
    for data in set1:
        f.write(str(data) +'\n') # python will convert \n to os.linesep
    f.close() # you can omit in most cases as the destructor will call if
    test = np.array(set1)


    np_arr = np.array(set1)
    iqr = np.subtract(*np.percentile(np_arr, [75, 25]))
    bin_width = 2 * iqr * len(set1) ** (-1/3) #  http://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule

    print("bin width: %s" % bin_width)
    plt.hist(set1, bins=np.arange(min(set1), max(set1) + bin_width, bin_width), normed=True)

    alpha, beta= analyze(test)

    x = np.arange(0, 1000, 0.1)
    s = hyperexp2_pdf(lam1, lam2, p, x)
    plt.plot(x,s)
    pylab.xlim([0,1000])
    pylab.ylim([0,0.0006])
    plt.show()


def hyperexp2_pdf(lam1,lam2,p,x):
    return p * lam1 * np.exp(-lam1 * x) + (1-p) * lam2 * np.exp(-lam2 * x)

def exponential_pdf(lam, x):
    if lam < 0:
        return 0
    else:
        return lam * np.exp(-lam*x)

def analyze(data, discrete=True, xmin=1.):
    model = mc.MCMC(_model(data))
    model.sample(5000)

    print 'alpha',mean(model.trace('alpha')[:])
    print 'beta',mean(model.trace('beta')[:])



    #return lam1, lam2, p


if __name__=='__main__':
    main()