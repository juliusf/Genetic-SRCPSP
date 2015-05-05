import deepThought.stats.Cdf as Cdf
import deepThought.stats.Pmf as Pmf
import numpy as np
import random
import bisect
import math
import sys


class Logger(object):
    log_level = 3
    @staticmethod
    def warning(message):
        if Logger.log_level > 1:
            Logger.log("warning", message)

    @staticmethod
    def error(message):
        Logger.log("error", message)

    @staticmethod
    def info(message):
        if Logger.log_level > 2:
            Logger.log("info", message)
    @staticmethod
    def debug(message):
        if Logger.log_level > 3:
            Logger.log("debug", message)
    @staticmethod
    def log(log_type, message):
        if log_type == "warning":
            print(PrintColors.WARNING),
            print("WARNING: "),
        elif log_type == "error":
            print(PrintColors.FAIL),
            print("ERROR: "),
        elif log_type == "info":
            print("INFO: "),
        elif log_type == "debug":
            print("DEBUG: ")
        print(message),
        print(PrintColors.ENDC)


class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class TypeConversion(object):
    @staticmethod
    def get_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


def pairs_list(list1, list2):
    """Produce all pairs for the two given lists"""
    for i1 in list1:
        for i2 in list2:
            yield i1, i2


def list_to_ccdf(list):
    array_x_axis, array_y_axis = list_to_cdf(list)
    return [array_x_axis, cdf_to_ccdf(array_y_axis)]

def list_to_cdf(list):
    array_hist = Pmf.MakeHistFromList(list)
    array_cdf = Cdf.MakeCdfFromHist(array_hist)
    array_x_axis, array_y_axis = array_cdf.Render()
    return [array_x_axis, array_y_axis]

def cdf_to_ccdf(p):
    ccdf = []
    for x in p:
        ccdf.append(1-x)
    return ccdf


def _cdf(weights):
    total = sum(weights)
    result = []
    cumsum = 0
    for w in weights:
        cumsum += w
        result.append(cumsum / total)
    return result

def choice(population, weights):
    assert len(population) == len(weights)
    cdf_vals = _cdf(weights)
    x = random.random()
    idx = bisect.bisect(cdf_vals, x)
    return population[idx]

Epsilon = sys.float_info.epsilon
def epsilon_compare(A, B):
    return (np.fabs(A) - np.fabs(B)) < np.finfo(np.double).eps

class DeepThoughtException(Exception):
    pass

class UnfeasibleScheduleException(DeepThoughtException):
    pass