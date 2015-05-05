__author__ = 'jules'

from deepThought.scheduler.scheduler import Scheduler
from deepThought.util import UnfeasibleScheduleException
import copy
from deepThought.util import Logger
"""
implementation of the resource based policy scheduling heuristic extended with the minimum forbidden set
"""
class DomainRB(Scheduler):
    def __init__(self, job, order_list,  ignore_infeasible_schedules=False):
        super(DomainRB, self).__init__(job)
        self.order_list = copy.copy(order_list)
        self.already_executed = []
        self.ignore_infeasible_schedules = ignore_infeasible_schedules
        self.eligble_to_run = []

    def _reschedule(self):
        new_tasks = []
        tasks_to_remove = []
        self.eligble_to_run = self.get_tasks_eligible_to_run()

        for task_id in self.order_list:
            if self.bottleneck_allows_execution(task_id, self.eligble_to_run):
                new_task = self.allocate_resources(self.tasks_to_do[task_id])
                self.eligble_to_run = self.get_tasks_eligible_to_run()
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

    def bottleneck_allows_execution(self, task_id, eligble_to_run):

        for resource  in self.resource_pool.values():
            if self.tasks_to_do[task_id] in resource.required_by:
                for competitor in eligble_to_run:
                    if competitor.id != task_id:
                        if competitor in resource.required_by:
                            if len(competitor.required_resources) > len(self.tasks_to_do[task_id].required_resources) or competitor.mean > self.tasks_to_do[task_id].mean:
                                return False
        return True