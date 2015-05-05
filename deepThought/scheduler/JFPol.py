__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.scheduler.RBRS import RBRS
from deepThought.scheduler.genetic.ListGA import ListGA
from deepThought.util import Logger
from deepThought.scheduler.DomainRB import DomainRB
"""
This class is the implementation of our own Algorithm which is based on the work by Ashtiani et al.
"""
class JFPol(Scheduler):
    def __init__(self, job):
        super(JFPol, self).__init__(job)
        self.job = job

    def _reschedule(self):
        return self.scheduler._reschedule()

    def initialize(self):
        super(JFPol, self).initialize()
        Logger.info("Generating initial Population with RBRS")
        initial_pop = self._generate_RBRS(self.job, 10)
        Logger.info("Applying ListGA to initial population")
        listGA = ListGA(self.job, initial_pop)
        task_list = listGA.do_it(150, 0.8, 0.2)[0]
        self.listGALog = listGA.get_logbook()

        self.scheduler = DomainRB(self.job, task_list,  ignore_infeasible_schedules=True)

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