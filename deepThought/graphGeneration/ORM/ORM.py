import math
import cPickle
from deepThought.util import Logger, TypeConversion, list_to_cdf
import deepThought.stats.phase_type as  ptdist
import numpy as np
from enum import Enum
import scipy.interpolate as interp

class DistributionType(Enum):
    FIXED = 1
    FITTED = 2
    PHASE = 3
    PRECOMPUTED = 4

def deserialize(file_path):
    Logger.info("loading data from file: %s" % file_path)
    job = cPickle.load(open(file_path, "rb"))
    Logger.info("loaded %s tasks" % (len(job.tasks.values())))
    Logger.info("loaded %s resources" % (len(job.resources.values())))
    Logger.info("loaded %s capabilities"  % (len(job.capabilities.values())))

    return job


class Job(object):
    def __init__(self):
        self.tasks = {}
        self.resources = {}
        self.capabilities = {}
        #note: this is only needed for the legacy scheduling algorithm.
        self.test_beds = {}
        self.already_initialized = False

    def initialize(self):
        for task in self.tasks.itervalues():
            task.initialize()


class Task:
    """
    representation of a task. For details see ER diagram
    """
    def __init__(self):
        self.name = ""
        self.mean = 0.0  # in seconds
        self.deviation = 0.0  # in seconds
        self.id = ""
        self.execution_time_limit = -1
        self.priority = ""
        self.required_resources = []
        self.execution_history = []
        self.number_of_executions = 0
        self.inverse_cdf = None
        self.pre_computed_execution_times = []
        self.distribution_type = None

    def initialize(self):
        # if we have historical data, use this to sample the distribution
        if len(self.execution_history) > 1:
            x,y = list_to_cdf(self.execution_history)
            self.inverse_cdf = interp.interp1d(y,x)
            if self.mean == None:
                self.mean = np.mean(self.execution_history)
            self.distribution_type = DistributionType.FITTED
        elif (self.mean is not None)  and (self.deviation is not None and self.deviation > 0): # if we have mean and variance, use that and the model
            self.inverse_cdf = ptdist.infer_inverted_cdf(self)
            self.distribution_type = DistributionType.PHASE
        else:
            self.distribution_type = DistributionType.FIXED # We don't have variance and mean. Just take the mean with a certain jitter.

    def get_next_execution_time(self):
        if self.distribution_type == DistributionType.FITTED:
             return self.inverse_cdf(np.random.uniform())
        elif self.distribution_type == DistributionType.PHASE:
            return self.inverse_cdf.rvs()
        elif self.distribution_type == DistributionType.FIXED:
            range = self.mean * 0.1 #ten percent jitter
            jitter = (2 * range) * np.random.random_sample() -range
            return self.mean + jitter
        else:
            assert  len(self.pre_computed_execution_times) > 0
            return self.pre_computed_execution_times.pop()

    def fill_pre_computed_execution_times(self, n):
        for i in range(n):
            self.pre_computed_execution_times.append(self.get_next_execution_time())
        self.distribution_type = DistributionType.PRECOMPUTED

    def compute_probability(self, number_of_executions, sum_execution_time_sq, sum_execution_times):

        n = TypeConversion.get_float(number_of_executions)
        sum_xi = TypeConversion.get_float(sum_execution_times)
        sum_xi_2 = TypeConversion.get_float(sum_execution_time_sq)
        self.number_of_executions = n

        if n is None:
            Logger.error("Cannot compute std deviation! Malformed input data!")
            self.mean = None
            self.deviation = None
            return

        if n == 0:
            self.mean = None
            self.deviation = None
            return

        if n == 1 and sum_xi is not None:
            self.mean = sum_xi
            self.deviation = 0
            return

        if n > 0 and sum_xi is None or sum_xi_2 is None:
            Logger.error("Cannot compute standard deviation! Malformed input data!")
            return

        #calculation of standard deviation
        tmp = sum_xi_2 - (1/n) * sum_xi ** 2
        s = math.sqrt((1/(n - 1)) * tmp)

        self.deviation = s
        #calculation of mean
        mean = (1/n) * sum_xi
        self.mean = mean


    def convert_execution_time_limit(self, string):
        if string is not None:
            if 'm' in string:
                assert string[-1] == 'm'
                string = string[:-1]
                self.execution_time_limit = int(string) * 60
                return
            elif 'h' in string:
                assert string[-1] == 'h'
                string = string[:-1]
                self.execution_time_limit = int(string) * 60 * 60
                return
            else:
                assert False, "should not happen"
        self.execution_time_limit = -1   #default value when there is no time limit

    #used to exclude scipy function from pickling
    def __getstate__(self):
        d = dict(self.__dict__)
        d['inverse_cdf'] = None
        return d

    def __setstate__(self, d):
        self.__dict__.update(d) # I *think* this is a safe way to do it

class Resource(object):
    def __init__(self):
        self.name = ""
        self.id = ""
        self.provided_capabilities = []
        self.is_testbed = False # needed for the reference Scheduler
        self.max_share_count = 0
        self.share_count = 0
        self.required_by = []

    def set_max_share_count(self, share_count):
        self.max_share_count = share_count
        self.share_count = share_count

class RequiredResource(object):
    """
    Meta Class used to describe a requirement for a device which needs the capabilities specified
    in the required_capabilities list.
    """

    def __init__(self):
        self.name = ""
        self.number_required = 0
        self.required_capabilities = []
        self.is_testbed = False
        self.fulfilled_by = []

class Capability(object):
    def __init__(self):
        self.id = ""
        self.name = ""
        self.attributes = []


class Attribute(object):
    def __init__(self):
        self.id = ""
        self.name = ""
        self.value = ""


