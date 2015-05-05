__author__ = 'jules'
import argparse
from deepThought.ORM.ORM import deserialize
from deepThought.util import Logger, TypeConversion
import sys
import pickle
from deepThought.multiprocessing.multicoreSimulation import process_job_parallel
from deepThought.simulator.simulator import simulate_schedule
from deepThought.scheduler.referenceScheduler import ReferenceScheduler
from deepThought.scheduler.optimizedDependencyScheduler import OptimizedDependencyScheduler
from deepThought.scheduler.PPPolicies import PPPolicies
from deepThought.scheduler.JFPol import JFPol
import time
import datetime
def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help="The pickle file containing the simulation data")
    arg_parser.add_argument("--cores", help="The number of cores to be used.")
    arg_parser.add_argument("--iter", help="The number of iterations per core.")
    arg_parser.add_argument("--out_folder", help="The folder to which result files are written")

    args = arg_parser.parse_args()
    try:
        job = deserialize(args.file)
    except IOError:
        Logger.error("The file specified was not found.")
        sys.exit(127)

    params = [

            {"listGAGen": 250,
              "listGACXp" : 1.0,
              "listGAMUTp": 0.5,
              "listNoList" : 10,
              "arcGAGen" : 100,
              "arcGACXp" : 0.5,
              "arcGAMUTp" : 0.01,
              "arcGAn_pairs" : 7,
              "arcGAno_p" : 10,
              "name" : "ArcGA mutp"
            },

            {"listGAGen": 250,
              "listGACXp" : 1.0,
              "listGAMUTp": 0.5,
              "listNoList" : 10,
              "arcGAGen" : 100,
              "arcGACXp" : 0.5,
              "arcGAMUTp" : 0.1,
              "arcGAn_pairs" : 7,
              "arcGAno_p" : 10,
              "name" : "ArcGA mutp"
            },

            {"listGAGen": 250,
              "listGACXp" : 1.0,
              "listGAMUTp": 0.5,
              "listNoList" : 10,
              "arcGAGen" : 100,
              "arcGACXp" : 0.5,
              "arcGAMUTp" : 0.3,
              "arcGAn_pairs" : 7,
              "arcGAno_p" : 10,
              "name" : "ArcGA mutp"
            },

            {"listGAGen": 250,
              "listGACXp" : 1.0,
              "listGAMUTp": 0.5,
              "listNoList" : 10,
              "arcGAGen" : 100,
              "arcGACXp" : 0.5,
              "arcGAMUTp" : 0.5,
              "arcGAn_pairs" : 7,
              "arcGAno_p" : 10,
              "name" : "ArcGA mutp"
            },



    ]
    run_multiple_opt(args, params)
def run_multiple_opt(args, parameter_sets):
    for idx, param in enumerate(parameter_sets):
        Logger.warning("running parameter set %s of %s" % (idx, len(parameter_sets)))
        run_optimization_process(args, param)

def run_optimization_process(args, parameters):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')
    try:
        job = deserialize(args.file)
    except IOError:
        Logger.error("The file specified was not found.")
        sys.exit(127)

    results, extremes = process_job_parallel("PPPolicies", job, TypeConversion.get_int(args.cores), TypeConversion.get_int(args.iter), parameters=parameters)
    parameters["results"] = results
    pickle.dump(parameters, open(args.out_folder + st + ".pickle", "wb"))

if __name__ == '__main__':
    main()