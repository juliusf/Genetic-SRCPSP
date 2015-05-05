__author__ = 'jules'

"""
Implementation of the regret-based biased random sampling for creation of initial population
"""

from deepThought.scheduler.scheduler import Scheduler, ScheduledTask
import deepThought.util as util
class RBRS(Scheduler):

    def __init__(self, job):
        super(RBRS, self).__init__(job)

    def _reschedule(self):

        """
        Implementation of the RBRS sampling algorithm. See Lecture 4 - NYU Stern pdf for details.
        """
        new_tasks = []
        while True:
            to_run = super(RBRS,self).get_tasks_eligible_to_run()

            if len(to_run) == 1:
                new_tasks.append(self.allocate_resources(to_run[0]))
                del self.tasks_to_do[to_run[0].id]
                continue

            if len(to_run)  < 1:
                break

            max = 0
            for task in to_run:
                if task.mean > max:
                    max = task.mean
            ws = []
            for task in to_run:
                ws.append(max - task.mean)

            c = 1 / sum(ws)

            ps = []

            for w in ws:
                ps.append(w * c)

            the_task = util.choice(to_run, ps)
            new_tasks.append(self.allocate_resources(the_task))
            del self.tasks_to_do[the_task.id]
        if len(new_tasks) > 0:
            return new_tasks

