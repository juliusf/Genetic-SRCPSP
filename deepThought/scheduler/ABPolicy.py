__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.util import UnfeasibleScheduleException
"""
This class represents ABPolicies. They are also known as priority lists.
"""
class ABPolicy(Scheduler):

    def __init__(self, job, order_list = None):
        super(ABPolicy, self).__init__(job)
        if order_list is not None:
            self.order_list = order_list
        else:
            self.order_list = [job.id in self.job.to_run.values()]

    def _reschedule(self):
        new_tasks = []

        for task_id in self.order_list:
            if task_id in self.tasks_to_do.keys():
               new_task = self.allocate_resources(self.tasks_to_do[task_id])
               if new_task is not None:
                    new_tasks.append(new_task)
                    del self.tasks_to_do[task_id]
               else:
                   break

        if len(new_tasks) == 0 and len(self.currently_assigned_resoruces) == 0 and len(self.tasks_to_do) is not 0:
            raise UnfeasibleScheduleException()
        return new_tasks