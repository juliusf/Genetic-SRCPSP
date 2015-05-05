import math
import numpy as np
import scipy.stats as stats
from scipy.interpolate import interp1d
import scipy
import scipy.signal


class SumRv(scipy.stats.rv_continuous):
    """
    Calculates the distribution for the sum of two random variables.

    Typically applied to see the effect of additive measurement error.
    Calculated by convolving the distributions - hence the error distribution
    is referred to as the 'kernel' of convolution.

    """
    def __init__(self, dist, kernel, delta,
                 dist_truncation=1e-4,
                 kernel_truncation=1e-4):
        self.input_dist = dist
        self.kernel = kernel

        #Calculate bounds for kernel support
        ksupp_low, ksupp_centre, ksupp_high = kernel.ppf((kernel_truncation,
                                                          0.5,
                                                          1. - kernel_truncation))
        ksupp_width = 2 * max(math.fabs(ksupp_centre - ksupp_low),
                              math.fabs(ksupp_high - ksupp_centre), )
        # Now we need to calculate the lowest odd number of delta-sized steps
        # which will enclose the ksupp_width
        # (Odd, so we have an even number above/below and a central sample point)
        # We add a delta either end in case the distribution has a sharp cutoff
        # which might be worth catching.
        n_kgrid_steps = math.ceil(ksupp_width / delta) + 2
        if n_kgrid_steps % 2 == 0:
            n_kgrid_steps += 1
        n_half_kgrid = (n_kgrid_steps - 1) / 2
        self.kgrid = np.arange(start=-n_half_kgrid * delta,
                               stop=n_half_kgrid * delta,
                               step=delta)

        # Now, ensure that the support for our output will be large enough
        # So as not to crop the tails of convolved dist
        support_low, support_high = dist.ppf((dist_truncation,
                                              1. - dist_truncation))
        support_low-= (ksupp_width/2.0+delta)
        support_high+= (ksupp_width/2.0+delta)
        n_support_steps = math.ceil((support_high - support_low)/delta)
        self.support = np.arange(start = support_low,
                                 stop = support_high,
                                 step = delta)


        # Strictly speaking, as PMF's these should both be multiplied by delta
        # But we omit 1 of the deltas here to avoid converting units back to
        # PDF after convolving
        dpmf = dist.pdf(self.support) #*delta (omitted for efficiency)
        kpmf = kernel.pdf(self.kgrid) * delta

        self.sum_pmf = scipy.signal.fftconvolve(dpmf, kpmf, 'same')
        self.sum_pdf = scipy.interpolate.interp1d(self.support, self.sum_pmf,
                                                     bounds_error=False,
                                                     fill_value=0.0)

        self.sum_cmf = np.cumsum(self.sum_pmf / np.sum(self.sum_pmf))
        self.sum_cdf = scipy.interpolate.interp1d(self.support, self.sum_cmf,
                                                     bounds_error=False,
                                                     fill_value=0.0)
        self.support_max = self.support.max()
        super(SumRv, self).__init__(name="SumRv")

    def _cdf(self, xvals):
        filled_vals =  self.sum_cdf(xvals)  # ensure that cdf[-1] = 1
        #Now, must replace any entries above upper bound with 1.0, not 0.0:
        filled_vals[xvals >= self.support_max] = 1.0
        return filled_vals

    def _pdf(self, xvals):
        return self.sum_pdf(xvals)

    def _stats(self):
        m = self.input_dist.stats("m") + self.kernel.stats("m")
        v = self.input_dist.stats("v") + self.kernel.stats("v")
        return m, v, 0., 0.
