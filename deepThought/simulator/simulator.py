__author__ = 'jules'

import simpy
import argparse
import sys
import copy
import deepThought.ORM.ORM as ORM

from deepThought.scheduler.referenceScheduler import ReferenceScheduler
from deepThought.scheduler.optimizedDependencyScheduler import OptimizedDependencyScheduler
from deepThought.scheduler.RBRS import RBRS
from deepThought.scheduler.PPPolicies import PPPolicies
from deepThought.scheduler.ABPolicy import ABPolicy
from deepThought.scheduler.JFPol import JFPol
from deepThought.simulator.simulationResult import *

from deepThought.simulator.simulationEntity import SimulationEntity
import random
import numpy as np
import time

import matplotlib.pylab as plt
import seaborn as sns
import datetime

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help="The pickle file containing the testData")
    arg_parser.add_argument("--scheduler", help="specifies the scheduler to be used. Default is referenceScheduler. \
                                                Other possible values: optimizedDependencyScheduler")
    arg_parser.add_argument("--output", help="specifies the file where the result should be written to")
    arg_parser.add_argument("--precomputeprobability", help="precomputes the probability data. follwed by a number")
    arg_parser.add_argument("--show_gen_log", help="controls whether to show historic genetic data")
    args = arg_parser.parse_args()

    #comment out if deterministic solutions are required
    np.random.seed(int(time.time()))
    random.seed()

    try:
        job = ORM.deserialize(args.file)
    except IOError:
        Logger.error("The file specified was not found.")
        sys.exit(127)

    assert isinstance(job, ORM.Job)


    Logger.debug("instantiating scheduler")
    schedulers = {
        ReferenceScheduler.__name__ : ReferenceScheduler,
        OptimizedDependencyScheduler.__name__ : OptimizedDependencyScheduler,
        RBRS.__name__ : RBRS,
        PPPolicies.__name__ : PPPolicies,
        ABPolicy.__name__  : ABPolicy,
        JFPol.__name__ : JFPol
    }

    if args.scheduler is None:
        scheduler = ReferenceScheduler(job)
    else:
        try:
            scheduler =  schedulers[args.scheduler](job)
        except KeyError:
            Logger.error("The scheduler specified does not exist.")
            sys.exit(127)

    if args.precomputeprobability is not None:
        Logger.debug("initializing job")
        job.initialize()
        Logger.info("Precomputing probability...")
        for i, task in enumerate(job.tasks.values()):
            Logger.info("Computing probabilities for task %s" % (i))
            task.fill_pre_computed_execution_times(int(args.precomputeprobability))

        Logger.info("Calculating Resource dependencies...")
        scheduler.initialize()
        job.already_initialized = True
        Logger.info("Writing to file")
        ORM.cPickle.dump(job, open(args.file, "wb"))
        sys.exit(0)

    start_time = datetime.datetime.now()
    if job.already_initialized == False:
        job.initialize()
        scheduler.initialize()
        Logger.debug("initializing job")



    Logger.debug("starting simulation...")
    result = simulate_schedule(scheduler)
    duration = datetime.datetime.now() - start_time
    Logger.warning("Simulation  complete. Duration: %s" % (duration))
    if args.show_gen_log is not None:
        log_list = scheduler.getListGALog()

        list_min = [datapoint['min'] for datapoint in log_list]
        list_max = [datapoint['max'] for datapoint in log_list]

        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        p1 = ax.plot(range(len(list_min)),list_min)
        p2 = ax.plot(range(len(list_max)),list_max)

        ax.set_xlabel("List GA Generation")
        ax.set_ylabel("fitness (execution time)")
        plt.legend( (p1[0], p2[0]), ('min', 'max'))
        ax = fig.add_subplot(2, 1, 2)

        log_arc = scheduler.getArcGALog()
        list_min =  [datapoint['min'] for datapoint in log_arc]
        list_max = [datapoint['max'] for datapoint in log_arc]

        for entry in list_max:
            if type(entry) == tuple:
                list_max.remove(entry)
        p1 = ax.plot(range(len(list_min)),list_min)
        p2 = ax.plot(range(len(list_max)),list_max)

        ax.set_xlabel("Arc GA Generation")
        ax.set_ylabel("fitness")
        plt.legend( (p1[0], p2[0]), ('min', 'max'))

        plt.show()

    if args.output is not None:
        try:
            save_simulation_result(result, args.output)
        except IOError:
            "The outputfile cannot be opened for writing."


def simulate_schedule(scheduler, stochastic=True, old_execution_history = None):
    env = simpy.Environment()
    #closure to capture scheduler Object
    def task_finished_callback(env):
        Logger.debug("Task finished. Current Simulation time: %s" % env.now)
        Logger.debug("%s tasks remaining" % len(scheduler.tasks_to_do))
        #as long as the scheduler has work to do, spawn tasks until resources are depleted
        while scheduler.has_next():
                SimulationEntity(env, scheduler.get_next(), task_finished_callback, stochastic, old_execution_history)

    #spawn tasks until resources are depleted
    while scheduler.has_next():
            SimulationEntity(env, scheduler.get_next(), task_finished_callback, stochastic, old_execution_history)
    env.run()
    if scheduler.no_tasks_executed != 44:
        Logger.warning("either too much or to few tasks executed")
    if scheduler.has_work_left():
        Logger.warning("The scheduler still has work left but can't continue! There is a Problem!")

    else:
        Logger.info("Simulation successful. Simulated Time: %s" % env.now)
    result = SimulationResult()
    result.total_time = env.now
    result.set_execution_history(scheduler.get_execution_history())

    return result

if __name__ == "__main__":
    main()