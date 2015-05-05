__author__ = 'jules'

import pymc
import numpy
import deepThought.ORM.ORM as ORM
numpy.random.seed(15)

job = ORM.deserialize("/tmp/output.pickle")

results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

set1 = results[0].execution_history
data = numpy.array(set1)

data = data / 10000

alpha = pymc.Uniform('alpha', lower=-100.0, upper=100.0)
beta = pymc.Gamma('beta', alpha=0.1, beta=0.001)

#data = pymc.rgamma( true_alpha, true_beta, size=(N_samples,) )

y = pymc.Gamma('y',alpha,beta,value=data,observed=True)
