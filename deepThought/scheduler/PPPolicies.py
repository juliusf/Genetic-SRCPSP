__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.scheduler.RBRS import RBRS
from deepThought.scheduler.genetic.ListGA import ListGA
from deepThought.scheduler.genetic.ArcGA import ArcGA
from deepThought.util import Logger
from deepThought.scheduler.MfssRb import MfssRB
"""
This class is the implementation of the Algorithm Proposed by Ashtiani et al.
"""
class PPPolicies(Scheduler):
    def __init__(self, job, parameters = None):
        super(PPPolicies, self).__init__(job)
        self.job = job
        if parameters is not None:
            self.param = parameters
        else:
            self.param = {"listGAGen": 2,
                          "listGACXp" : 1.0,
                          "listGAMUTp": 0.5,
                          "listNoList" : 10,
                          "arcGAGen" : 100,
                          "arcGACXp" : 0.5,
                          "arcGAMUTp" : 0.1,
                          "arcGAn_pairs" : 7,
                          "arcGAno_p" : 10}


    def _reschedule(self):
        return self.scheduler._reschedule()

    def initialize(self):
        super(PPPolicies, self).initialize()
        Logger.info("Generating initial Population with RBRS")
        initial_pop = self._generate_RBRS(self.job, self.param["listNoList"])
        Logger.info("Applying ListGA to initial population")
        listGA = ListGA(self.job, initial_pop)
        task_list = listGA.do_it(self.param["listGAGen"], self.param["listGACXp"], self.param["listGAMUTp"])[0]
        self.listGALog = listGA.get_logbook()
        if self.param["arcGAGen"] > 0:
            arcGA = ArcGA(self.job, task_list)
            arc_list = arcGA.do_it(self.param["arcGAGen"], self.param["arcGACXp"],self.param["arcGAMUTp"])[0] #2, 0.5, 0.1
            #Logger.warning("len arc list: %s" % (len(arc_list)))
            self.arcGALog = arcGA.get_logbook()

            self.scheduler = MfssRB(self.job, task_list, arc_list, ignore_infeasible_schedules=True)
        else:
            self.arcGALog = []
            self.arcGALog.append({"min":0, "max":0})

            self.scheduler = MfssRB(self.job, task_list, [], ignore_infeasible_schedules=True)

    def has_next(self):
        return self.scheduler.has_next()

    def get_next(self):
        self.no_tasks_executed +=1
        return self.scheduler.get_next()

    def has_work_left(self):
        return self.scheduler.has_work_left()

    def get_execution_history(self):
        return self.scheduler.get_execution_history()

    def _generate_RBRS(self, job, n):
        import deepThought.simulator.simulator as sim # ugly circular dependency
        inital_population = []
        for i in range(n):
            rbrs_scheduler = RBRS(job)
            result = sim.simulate_schedule(rbrs_scheduler)
            inital_population.append(result.execution_history)
        return inital_population
    def getListGALog(self):
        return self.listGALog
    def getArcGALog(self):
        return self.arcGALog