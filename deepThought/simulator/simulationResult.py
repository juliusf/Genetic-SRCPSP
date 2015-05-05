__author__ = 'jules'

from deepThought.util import Logger
import cPickle


class SimulationResult(object):
    def __init__(self):
        self.total_time = 0
        self.execution_history = []
        self.parallelity_factor = 1
        self.jobs = {}

    def set_execution_history(self, execution_history):
        self.execution_history = execution_history
        for job in execution_history:
            self.jobs[job.id] = job
            job.scheduler = None

def save_simulation_result(result, output_file):
    Logger.info("writing simulation result to file: %s" % output_file)
    cPickle.dump(result, open(output_file, "wb"))


def load_simulation_result(file_path):
    Logger.info("loading simulation result from file: %s " % file_path )
    return cPickle.load(open(file_path, "rb"))
