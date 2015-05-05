__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.util import UnfeasibleScheduleException
import copy
from deepThought.util import Logger
"""
implementation of the resource based policy scheduling heuristic extended with the minimum forbidden set
"""
class MfssRB(Scheduler):
    def __init__(self, job, order_list, mfss,  ignore_infeasible_schedules=False):
        super(MfssRB, self).__init__(job)
        self.order_list = copy.copy(order_list)
        self.mfss = mfss
        self.already_executed = []
        self.ignore_infeasible_schedules = ignore_infeasible_schedules

    def _reschedule(self):
        new_tasks = []
        tasks_to_remove = []
        for task_id in self.order_list:
            if self.mfss_allows_execution(task_id):
                new_task = self.allocate_resources(self.tasks_to_do[task_id])
                if new_task == None:
                    pass
                else:
                    new_tasks.append(new_task)
                    del self.tasks_to_do[task_id]
                    tasks_to_remove.append(task_id)
                    self.already_executed.append(task_id)
        [self.order_list.remove(task) for task in tasks_to_remove]

        if len(new_tasks) == 0 and len(self.currently_assigned_resoruces) == 0 and len(self.tasks_to_do) > 0:
            if not self.ignore_infeasible_schedules:
                raise UnfeasibleScheduleException()
            else:
                Logger.warning("Unfeasible schedule encountered. Ignoring mfss")
                for task_id in self.order_list:
                    new_task = self.allocate_resources(self.tasks_to_do[task_id])
                    if new_task == None:
                        pass
                    else:
                        new_tasks.append(new_task)
                        del self.tasks_to_do[task_id]
                        tasks_to_remove.append(task_id)
                        self.already_executed.append(task_id)
            [self.order_list.remove(task) for task in tasks_to_remove]
        return new_tasks

    def mfss_allows_execution(self, task_id):
        for set in self.mfss:
            if task_id == set[1] and set[0] not in self.already_executed:
                return False
        return True