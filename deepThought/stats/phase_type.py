__author__ = 'jules'

import numpy as np

from scipy.stats import uniform

from customDistributions import Hyperexp2_gen, Erlangk_gen, Gamma, BranchingErlang, TruncatedErlangk_gen, MixtureNormUni, TruncatedHyperexp2

import math

def infer_distribution(job):

    X = np.array(job.execution_history)
    mean = np.mean(X)
    cx = np.sqrt(np.var(X)) / mean
    cxsqrd = cx * cx

    if cxsqrd >= 1:
        return approximate_truncated_hyperexp2(cxsqrd, mean, job)
        #return approximate_hyperexp2(cxsqrd, mean)

    elif cxsqrd >= 0.5:
        return approximate_truncated_erlangk(cxsqrd, mean, job)
        #return approximate_erlangk(cxsqrd, mean)

    else:

        #return approximate_gamma(cxsqrd, mean)
        #return approximate_truncated_erlangk(cxsqrd, mean, job)
        #return approximate_erlangk(cxsqrd, mean)
        #return approximate_mix_gaussian_uniform(X)
        return approximate_uniform(cxsqrd, mean)

def infer_inverted_cdf(task):
    cx = task.deviation / task.mean
    cxsqrd = cx * cx

    #truncated distribution
    if task.execution_time_limit != -1:
        if cxsqrd >= 1:
           return approximate_truncated_hyperexp2(cxsqrd, task.mean, task)
        else:
            return approximate_truncated_erlangk(cxsqrd, task.mean, task)
    else:
        if cxsqrd >=1:
            return approximate_hyperexp2(cxsqrd,task.mean)
        else:
            return approximate_erlangk(cxsqrd, task.mean)


def approximate_mix_gaussian_uniform(X):
    mu = np.mean(X)
    sigma = np.var(X)
    p = 0.1
    a = 0.0
    b = (2 * mu) * (1-p)  #check whether this could be approximated otherwise

    mu1 = mu / p
    mu2 = (1.0/2.0) * (a+b)
    sigma2 = np.sqrt( (1.0/12.0) * ((b-a)**2) )
    #sigma1 = np.sqrt( -(mu1)**2 + (mu2**2) - ((mu2**2)/p) + (sigma2**2) + (sigma /p) - (sigma2**2)/p )
    sigma1 = np.sqrt(-mu1**2 - sigma2 ** 2 + (sigma2 / p) + (mu2/p) + (sigma/p)) # produces complex results! can't be handled by np.sqrt()
    dist = MixtureNormUni(p, sigma1, mu, a, b)
    dist.name = "gaussian uniform mixture"
    return dist


def approximate_uniform(cxsqrd, mean):
    b = 2 * mean
    dist = uniform(scale=b)
    dist.name = "uniform"
    return dist

def approximate_branching_erlang(cxsqrd, mean):
    k =int(math.ceil(1.0/cxsqrd))
    a = ( 2*k*cxsqrd + (k - 2) - np.sqrt( (k**2) + 4 - 4 * k * cxsqrd ))/( 2*(k-1)*(cxsqrd+1) )
    mu = (k - a * (k-1))/mean
    dist = BranchingErlang(a,mu,k)
    dist.name = "Branching Erlang"
    return dist

def approximate_lognorm(cxsqrd, mean):
    pass
    #dist = lognorm([sigma], loc=mu)
    #dist.name = "lognorm"
    #return dist

def approximate_erlangk(cxsqrd, mean):
    k = 2
    while True: #solve it like a hacker!
        if ( (1.0/k) <= cxsqrd) and ( 1.0 / (k -1.0)) >= cxsqrd:
            break
        else:
            k +=1

    #p = (1.0/ (1 + cxsqrd)) * ( k * cxsqrd - (k * (1 + cxsqrd) - (k ** 2) * cxsqrd)**(1.0/2.0) )
    p = (1.0/ (1 + cxsqrd)) * ( k * cxsqrd -np.sqrt(k*(1+cxsqrd) -k*k*cxsqrd  ))
    mu = (k - p) / mean
    dist =Erlangk_gen("Erlang_k-1,k", mu=mu, p=p, k=k)
    dist.name = "Erlangk, k-1"
    return dist

def approximate_truncated_erlangk(cxsqrd, mean, job):
    a = 0
    if job.execution_time_limit == -1:
        b = 86400 # 24h
    else:
        b = job.execution_time_limit

    k = 2
    while True: #solve it like a hacker!
        if ( (1.0/k) <= cxsqrd) and ( 1.0 / (k -1.0)) >= cxsqrd:
            break
        else:
            k +=1


    p = (1.0/ (1 + cxsqrd)) * ( k * cxsqrd -np.sqrt(k*(1+cxsqrd) -k*k*cxsqrd  ))
    mu = (k - p) / mean
    dist =TruncatedErlangk_gen("Erlang_k-1,k", mu=mu, p=p, k=k, a=a,b=b)
    dist.name = "Truncated Erlangk, k-1"
    return dist

def approximate_hyperexp2(cxsqrd, mean):
    p1 = (1.0/2.0) * (1.0 + np.sqrt( ( cxsqrd - 1.0) / (cxsqrd + 1.0)) )
    p2 = 1.0 - p1

    mu1 = (2.0 * p1) / mean
    mu2 = (2.0 * p2) / mean
    dist= Hyperexp2_gen("bar", lambda1=mu1, lambda2=mu2, p=p1)
    dist.name = "Hyperexp2"
    return dist

def approximate_truncated_hyperexp2(cxsqrd, mean, job):
    a = 0
    if job.execution_time_limit == -1:
        b = 86400 # 24h
    else:
        b = job.execution_time_limit

    p1 = (1.0/2.0) * (1.0 + np.sqrt( ( cxsqrd - 1.0) / (cxsqrd + 1.0)) )
    p2 = 1.0 - p1

    mu1 = (2.0 * p1) / mean
    mu2 = (2.0 * p2) / mean
    dist= TruncatedHyperexp2("bar", lambda1=mu1, lambda2=mu2, p=p1, a=a, b=b)
    dist.name = "truncated Hyperexp2"
    return dist
def approximate_gamma(cxsqrd, mean):
    mu = 1 / mean
    alpha = 1 / cxsqrd
    dist = Gamma(alpha, mu)
    dist.name = "Gamma"
    return dist
