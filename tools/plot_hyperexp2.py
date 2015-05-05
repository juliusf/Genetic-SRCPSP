__author__ = 'jules'


import matplotlib.pylab as plt
import numpy as np
import deepThought.ORM.ORM as ORM
from deepThought.util import list_to_ccdf
from deepThought.stats import Pmf
def hyperexp2(lambda1, lambda2, p, x):
        return p * lambda1 * np.exp(-lambda1 * x) + (1-p) * lambda2 * np.exp(-lambda2 * x)

def hyperexp3(lambda1, lambda2, lambda3, alpha, beta,x):
    t1 = alpha * lambda1 * np.exp(-lambda1 * x)
    t2 = beta * lambda2 * np.exp(-lambda2 *x)
    t3 = (1 - (alpha + beta)) * lambda3 * np.exp(-lambda3 *x)
    return t1 + t2 + t3


job = ORM.deserialize("/tmp/output.pickle")
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)


set1 = results[0].execution_history
np_arr = np.array(set1)
iqr = np.subtract(*np.percentile(np_arr, [75, 25]))
bin_width = 2 * iqr * len(set1) **(-1/3) #  http://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule


print("bin width: %s" % bin_width)
#ax.hist(set1, bins=np.arange(min(set1), max(set1) + bin_width, bin_width), normed=True)

x, y = list_to_ccdf(set1)

ax.plot(x,y, "-r")
x = np.arange(0, 100000, 0.1)


#s = hyperexp2(1.04444444e-03, 1.13888889e+00,  7.00000000e-01, x)
#x,y = list_to_ccdf(s.tolist())


#ax.plot(x,y, linewidth=3)
for p in np.arange(0.1, 1, 0.1):
    y = hyperexp2(15.04444444e-05, 15.13888889e+02,  0.5, x, 9)
    ax.plot(x,y)
    pass
#for alpha in np.arange(0.1, 0.4, 0.1):
#    for beta in np.arange(0.1,0.4,0.1):
#        plt.plot(x,hyperexp3(1/100,100,400,alpha, beta,x))

#plt.xlim([0,100])
#plt.ylim([0,0.001])
ax.set_xscale("log")
ax.set_yscale("log")
plt.show()