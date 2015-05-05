#!/usr/bin/env python
from  multiprocessing import Process, Manager
import pickle
import numpy
import time
from deepThought.ORM.ORM import deserialize
from deepThought.util import Logger, TypeConversion
from deepThought.simulator.simulator import simulate_schedule
from deepThought.scheduler.referenceScheduler import ReferenceScheduler
from deepThought.scheduler.optimizedDependencyScheduler import OptimizedDependencyScheduler
from deepThought.scheduler.PPPolicies import PPPolicies
from deepThought.scheduler.JFPol import JFPol
import argparse
import sys
import random
import datetime
from progressbar import ProgressBar
import os

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help="The pickle file containing the simulation data")
    arg_parser.add_argument("--cores", help="The number of cores to be used.")
    arg_parser.add_argument("--iter", help="The number of iterations per core.")
    arg_parser.add_argument("--out_extremes", help="The file the extreme values should be written to.")
    arg_parser.add_argument("--out_results", help="The file all the lambdas should be written to.")
    arg_parser.add_argument("--scheduler", help="specifies the scheduler to be used. Default is referenceScheduler. \
                                                Other possible values: optimizedDependencyScheduler")
    args = arg_parser.parse_args()
    try:
        job = deserialize(args.file)
    except IOError:
        Logger.error("The file specified was not found.")
        sys.exit(127)
    results, extremes = process_job_parallel(args.scheduler, job, TypeConversion.get_int(args.cores), TypeConversion.get_int(args.iter))

    if args.out_extremes is not None:
        pickle.dump(extremes, open(args.out_extremes, "wb"))

    if args.out_results is not None:
        pickle.dump(results, open(args.out_results, "wb"))


def process_job_parallel(scheduler, job, nr_cores, nr_iter, parameters = None):
    Logger.log_level = 2
    processes = []
    manager = Manager()
    return_values = manager.dict()
    extremes = manager.dict()
    start_time = datetime.datetime.now()
    for i in range(nr_cores):
        p = Process(target=worker, args=(i, nr_cores, scheduler, job, nr_iter, return_values, extremes, parameters,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    #reduce
    results = []
    for value in return_values.values():
        for entry in value:
            results.append(entry)

    min = None
    max = None

    for extreme in extremes.values():
        if min is None or extreme[0].total_time < min.total_time:
            min = extreme[0]
        if max is None or extreme[1].total_time > max.total_time:
            max = extreme[1]
    Logger.warning("Min: %s" % min.total_time)
    Logger.warning("Max: %s" % max.total_time)

    duration = datetime.datetime.now() - start_time
    Logger.warning("Simulation  complete. Duration: %s" % (duration))
    return results, (min,max)

def worker(id, nr_cores, scheduler, job, n, return_values, extremes, parameters=None):
    os.system("taskset -p 0xFFFFFFFF %d" % os.getpid())
    pbar = ProgressBar(maxval=n).start()
    Logger.info("spawning worker id %s" % id)
    numpy.random.seed(id + int(time.time()))
    random.seed()
    #Logger.log_level = 2
    results = []
    min = None
    max = None
    if job.already_initialized == True:
        for task in job.tasks.values():
            size = len(task.pre_computed_execution_times) / nr_cores
            task.pre_computed_execution_times = task.pre_computed_execution_times[id*size:(id +1)*size]
    Scheduler = schedulerForName(scheduler) #gives us the correct class to use

    for i in range(0, n):
        if id == 0:
            pbar.update(i)

        scheduler = Scheduler(job, parameters)
        if job.already_initialized == False:
            job.initialize()
            scheduler.initialize()

        result = simulate_schedule(scheduler)
        results.append(result.total_time)
        if min is None or  result.total_time < min.total_time:
            min = result
        if max is None or  result.total_time > max.total_time:
            max = result

    return_values[id] = results
    extremes[id] = (min, max)
    if id == 0:
        pbar.finish()

def schedulerForName(name):
    schedulers = {ReferenceScheduler.__name__ : ReferenceScheduler, OptimizedDependencyScheduler.__name__ : OptimizedDependencyScheduler,
                  PPPolicies.__name__ : PPPolicies,
                  JFPol.__name__ : JFPol}
    if name is None:
        scheduler = ReferenceScheduler
    else:
        try:
            scheduler =  schedulers[name]
        except KeyError:
            Logger.error("The scheduler specified does not exist.")
            sys.exit(127)
    return scheduler

if __name__ == '__main__':
    main()
