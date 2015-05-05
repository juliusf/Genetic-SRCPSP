__author__ = 'jules'

import cProfile
import deepThought.ORM.ORM as ORM
from deepThought.scheduler.PPPolicies import PPPolicies
import deepThought.simulator.simulator as simulator

def main():
    job = ORM.deserialize("/tmp/output.pickle")
    scheduler = PPPolicies(job)
    job.initialize()
    scheduler.initialize()
    command = "simulator.simulate_schedule(scheduler)"
    cProfile.runctx( command, globals(), locals(), filename="/tmp/simulator.profile" )

if __name__ == "__main__":
    main()