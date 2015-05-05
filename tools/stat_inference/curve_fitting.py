import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import curve_fit
import deepThought.ORM.ORM as ORM
from deepThought.util import list_to_cdf

def func(x, p, lam1, lam2):
    #return p * np.exp(-lam1 * x) + (1.0-p) * np.exp(-lam2 * x)\
    return lam1*np.cos(lam2*x)+lam2*np.sin(lam1*x)

# user provides LaTeX code for function for later use:
fitEquation = r"$\displaystyle\mathrm{fit} =  a e^{-b t} + c$"

#N=100
#x = np.linspace(0,4, N) ## I arbitrarily used N = 100 points

#y = func(x, 2.5, 1.3, 0.5)  # base function
#yn = y + 0.2*np.random.normal(size=len(x))  # noise added

job = ORM.deserialize("/tmp/output.pickle")
results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

jobs = []
for x in results:
    if len(x.execution_history) > 2:
        jobs.append(x.execution_history)

x_data, y_data = list_to_cdf(jobs[1])
x_data = np.array(x_data)
y_data = np.array(y_data)
dx = (max(x_data) - min(x_data))/len(x_data)

popt, pcov = curve_fit(func, x_data, y_data)  # popt = OPTimal Parameters for fit; COVariance matrix
print popt
sigma = np.sqrt([pcov[0,0], pcov[1,1], pcov[2,2]]) # sqrt(diag elements) of pcov are the 1 sigma deviations

values = np.array([
    func(x_data, popt[0] + sigma[0], popt[1] + sigma[1], popt[2] + sigma[2]),
    func(x_data, popt[0] + sigma[0], popt[1] - sigma[1], popt[2] + sigma[2]),
    func(x_data, popt[0] + sigma[0], popt[1] + sigma[1], popt[2] - sigma[2]),
    func(x_data, popt[0] + sigma[0], popt[1] - sigma[1], popt[2] - sigma[2]),
    func(x_data, popt[0] - sigma[0], popt[1] + sigma[1], popt[2] + sigma[2]),
    func(x_data, popt[0] - sigma[0], popt[1] - sigma[1], popt[2] + sigma[2]),
    func(x_data, popt[0] - sigma[0], popt[1] + sigma[1], popt[2] - sigma[2]),
    func(x_data, popt[0] - sigma[0], popt[1] - sigma[1], popt[2] - sigma[2])
    ])

fitError = np.std(values, axis=0)

nSigma = 3
mpl.rc('text', usetex=True)
mpl.rc('font', family='serif')
mpl.rc('xtick', labelsize=20)
mpl.rc('ytick', labelsize=20)
mpl.rcParams['xtick.major.pad'] = 10
mpl.rcParams['ytick.major.pad'] = 10

fig = plt.figure(figsize=(12,8), dpi=100, facecolor='w', edgecolor='k')
ax = fig.add_subplot(111)
ax.xaxis.labelpad = 20
ax.yaxis.labelpad = 20
curveFit = func(x_data,popt[0], popt[1], popt[2] )
plt.plot(x_data, y_data, 'o')
plt.hold(True)
plt.plot(x_data, curveFit,
    linewidth=2.5,
    color = 'red',
    alpha = 0.6,
    label = fitEquation)
"""
plt.bar(left=x_data,
    height = 2*nSigma*fitError,
    width=dx,
    bottom = curveFit - nSigma*fitError,
    orientation = 'vertical',
    alpha=0.04,
    color = 'purple',
    edgecolor = None,t
    label = r"$\displaystyle \pm 3\sigma\;\;\mathrm{errorBars}$")

plt.plot(x_data, curveFit+fitError,
    linewidth = 1.0,
    alpha = 0.5,
    color = 'red',
    label = r"$\displaystyle  \pm 1\sigma\;\;\mathrm{error}$")

plt.plot(x_data, curveFit-fitError,
    linewidth = 1.0,
    alpha = 0.5,
    color = 'red')
props = dict(boxstyle='round', facecolor='wheat', alpha=0.2)
plt.text(3.2, 1.0,
    ("$\mathrm{curve fit\;\;values:\;}$\n a = %.3f\t $\pm$ %.3f\n b = %.3f\t $\pm$ %.3f \n c = %.3f\t $\pm$ %.3f"
    % (popt[0], sigma[0], popt[1], sigma[1], popt[2], sigma[2])), fontsize=16, bbox=props )
plt.xlabel(r'\textrm{time (s)}', fontsize=24)
plt.ylabel(r'\textrm{temperature (K)}',fontsize=24)
plt.title(r"Exponential fit with $\pm 1\sigma$ and $\pm 3\sigma$ fit errors",
      fontsize=28, color='k')
ax.legend(fontsize=18)
"""
#plt.savefig('3sigmaPlot.pdf', figsize=(6,4), dpi=600)
plt.show()