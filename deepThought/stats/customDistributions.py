__author__ = 'jules'
from  scipy.stats import rv_continuous
import numpy as np
from scipy.misc import factorial
from scipy.special import gammainc, gamma, erf
from scipy.linalg import expm
class Hyperexp2_gen(rv_continuous):
    def __init__(self,name,  lambda1, lambda2, p):
        rv_continuous.__init__(self, name)
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.p = p

    def _pdf(self, x):
            return self.p * self.lambda1 * np.exp(-self.lambda1 * x) + (1-self.p) * self.lambda2 * np.exp(-self.lambda2 * x)

    def _cdf(self, x):
        return  1 - (self.p * np.exp(-self.lambda1*x) + (1-self.p) * np.exp(-self.lambda2* x))

class TruncatedHyperexp2(rv_continuous):
    def __init__(self,name,  lambda1, lambda2, p, a,b):

        rv_continuous.__init__(self, name)
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.p = p
        self.a = a
        self.b = b

    def _cdf(self, x):
        a = self.a
        b = self.b
        lambda1 = self.lambda1
        lambda2 = self.lambda2
        p = self.p
        def F(x):
            return p*(1-np.exp(-lambda1*x))+(1-p)*(1-np.exp(-lambda2*x))

        return _compute_truncated_CDF(F, a, b, x)

class MixtureNormUni(rv_continuous):
    def __init__(self, p, sigma1, mu1, a, b):
        rv_continuous.__init__(self)
        self.p = p
        self.a = a
        self.b = b
        self.sigma1 = sigma1
        self.mu1 = mu1

   # def _pdf(self, x, *args):
   #     return self.p1 * self.dist1.pdf(x) + (1-self.p1) * self.dist2.pdf(x)

    def _cdf(self, x, *args):
        a = self.a
        b = self.b
        p = self.p
        sigma1 = self.sigma1
        mu1 = self.mu1

        prod = 1 / (a-b)
        sumand1 = -((a*p)/4) * np.sqrt(2) * erf( (1/sigma1) * (mu1 -x))
        sumand2 =  ((b*p)/4) * np.sqrt(2) * erf( (1/sigma1) * (mu1 -x))

        sumand = sumand1 + sumand2 + (p*x -x )

        return prod * sumand

class MixtureNormNorm(rv_continuous):
    def __init__(self, p, sigma1, mu1, sigma2, mu2):
        rv_continuous.__init__(self)
        self.p = p
        self.sigma2 = sigma2
        self.sigma2 = sigma2
        self.sigma1 = sigma1
        self.mu1 = mu1

   # def _pdf(self, x, *args):
   #     return self.p1 * self.dist1.pdf(x) + (1-self.p1) * self.dist2.pdf(x)

    def _cdf(self, x, *args):
        p = self.p
        sigma1 = self.sigma1
        mu1 = self.mu1
        sigma2 = self.sigma2
        mu2 = self.mu2

        prod = np.sqrt(2)/4
        sumand1 = - p * erf( (1/sigma1) * (mu1 -x) )
        sumand2 =   p * erf( (1/sigma2) * (mu2 -x) )
        sumand3 = - erf(  (1/(sigma2**2)) * (mu2 -x) )


        return prod * (sumand1 + sumand2 + sumand3)
class Erlangk_gen(rv_continuous):
    def __init__(self, name , mu,  p, k):
        rv_continuous.__init__(self, name)
        self.mu = mu
        self.k = k
        self.p = p

    def _pdf(self, x):
        k1 =   self.p * self.mu * (  ( (self.mu * x)** (self.k -2)) / factorial(self.k - 2) ) * np.exp(-self.mu*x)

        k2 = (1 - self.p) * self.mu * ( ( (self.mu *x )** (self.k -1)) / factorial(self.k -1) ) * np.exp(-self.mu*x)

        return k1 + k2

    def _cdf(self, x):
        k = self.k
        mu = self.mu
        p = self.p
        return (k / factorial(k)) * (k*p*gammainc(k-1, mu*x) - p*gammainc(k, mu*x) - p*gammainc(k-1,mu*x) + gammainc(k, mu*x))

class TruncatedErlangk_gen(rv_continuous):
    def __init__(self, name , mu,  p, k, a, b):
        rv_continuous.__init__(self, name)
        self.mu = mu
        self.k = k
        self.p = p
        self.a = a
        self.b = b

    def _cdf(self, x):
        k = self.k
        mu = self.mu
        p = self.p
        a = self.a
        b = self.b
        def F(x):
            return (k / factorial(k)) * (k*p*gammainc(k-1, mu*x) - p*gammainc(k, mu*x) - p*gammainc(k-1,mu*x) + gammainc(k, mu*x))
        return _compute_truncated_CDF(F, a,b,x)

class Erlang_1k(rv_continuous):
    def __init__(self, name , mu,  p, k):
        rv_continuous.__init__(self, name)
        self.mu = mu
        self.k = k
        self.p = p

    def  _cdf(self, x):
        k = self.k
        mu = self.mu
        p = self.p
        sumand = (k * (-p +1) * gamma(k) * gammainc(k,mu*x)) / ( (factorial(k-1)*gamma(k+1)))

        if mu == 0:
            return sumand + mu*p*x
        else:
            return sumand + mu*p * (- (1/mu) * np.exp(-mu*x))

class Erlang(rv_continuous):
    def __init__(self,k, mu):
        rv_continuous.__init__(self, "erlang")
        self.mu = mu
        self.k = k

    def  _cdf(self, x):
        k = self.k
        mu = self.mu
        sum = 0
        for j in range(0, k-1):
            sum += ((k*mu*x)**j)/(factorial(j))

        return 1 - np.exp(-k*mu*x) * sum

class Gamma(rv_continuous):
    def __init__(self,alpha, mu):
        rv_continuous.__init__(self, "gamma")
        self.alpha = alpha
        self.mu = mu

    def  _cdf(self, x):
        alpha = self.alpha
        mu = self.mu


        return (1 / gamma(alpha)) * gammainc(alpha, mu * x)

class BranchingErlang(rv_continuous):
    #or cox distribution
    def __init__(self,a, mu,k ):
        rv_continuous.__init__(self, "gamma")
        self.a = a
        self.mu = mu
        self.k = k

    def  _cdf(self, x):
        a = self.a
        mu = self.mu
        k = self.k

        s = np.zeros((k,k,))
        for i in range(k):
            s[i][i] = -mu
            if i < k-1:
                s[i][i+1] = a*mu

        alpha = np.zeros(k)
        one_vec = np.ones(k)
        alpha[0] = 1

        result = np.zeros(len(x))
        for t in range(len(x)):
            result[t] = 1 - np.dot( np.dot(alpha, expm(s * x[t])), one_vec)

        return result

def _compute_truncated_CDF(cdf, a, b, x):
        #For notes on truncation see: http://www.encyclopediaofmath.org/index.php?title=Truncated_distribution&oldid=12465
        Fx = cdf(x)
        Fa = cdf(a)
        Fb = cdf(b)
        return ( Fx - Fa) / (Fb - Fa)