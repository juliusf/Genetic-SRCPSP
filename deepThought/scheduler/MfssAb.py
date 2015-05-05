__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.util import UnfeasibleScheduleException
from deepThought.util import Logger
"""
This class represents ABPolicies. They are also known as priority lists. This is extended with the minimum feasible set
"""
class MfssAB(Scheduler):

    def __init__(self, job, mfss, order_list = None, ignore_infeasible_schedules=False):
        super(MfssAB, self).__init__(job)
        if order_list is not None:
            self.order_list = order_list
        else:
            self.order_list = [job.id in self.job.to_run.values()]
        self.mfss = mfss
        self.ignore_infeasible_schedules = ignore_infeasible_schedules

    def _reschedule(self):
        new_tasks = []

        for task_id in self.order_list:
            if self.mfss_allows_execution(task_id) and task_id in self.tasks_to_do.keys():
               new_task = self.allocate_resources(self.tasks_to_do[task_id])
               if new_task is not None:
                    new_tasks.append(new_task)
                    del self.tasks_to_do[task_id]
               else:
                   break

        if len(new_tasks) == 0 and len(self.currently_assigned_resoruces) == 0 and len(self.tasks_to_do) is not 0:
            if self.ignore_infeasible_schedules == False:
                raise UnfeasibleScheduleException()
            else:
                Logger.warning("unfeasible schedule encountered. Ignoring mfss")
                for task_id in self.tasks_to_do.keys():
                    new_task = self.allocate_resources(self.tasks_to_do[task_id])
                    if new_task is not None:
                        new_tasks.append(new_task)
                        del self.tasks_to_do[task_id]
                        break

        return new_tasks

    def mfss_allows_execution(self, task_id):
        for set in self.mfss:
            if task_id == set[1] and set[0] in self.tasks_to_do.keys():
                return False
        return True