__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.util import UnfeasibleScheduleException
import copy
"""
This class represents ABPolicies. They are also known as priority lists.
"""
class RBPolicy(Scheduler):

    def __init__(self, job, order_list = None):
        super(RBPolicy, self).__init__(job)
        if order_list is not None:
            self.order_list = copy.deepcopy(order_list) #maybe this can be done better
        else:
            self.order_list = copy.copy([job.id in self.job.to_run.values()])

    def _reschedule(self):
        new_tasks = []
        tasks_to_remove = []
        for task_id in self.order_list:
                new_task = self.allocate_resources(self.tasks_to_do[task_id])
                if new_task != None:
                    new_tasks.append(new_task)
                    del self.tasks_to_do[task_id]
                    tasks_to_remove.append(task_id)


        [self.order_list.remove(task) for task in tasks_to_remove]
        if len(new_tasks) > 0:
            return new_tasks