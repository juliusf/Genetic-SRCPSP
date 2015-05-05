
from deepThought.scheduler.scheduler import Scheduler, ScheduledTask
import deepThought.ORM.ORM as ORM

class ReferenceScheduler(Scheduler):
    def __init__(self, job, parameters = None):
        super(ReferenceScheduler, self).__init__(job)
    def _reschedule(self):
        list_of_new_tasks = []

        for task in self.tasks_to_do.values():
            task_or_none = self.allocate_resources(task)

            if task_or_none is not None:
                list_of_new_tasks.append(task_or_none)

        for task in list_of_new_tasks:
            del self.tasks_to_do[task.id]

        if len(list_of_new_tasks) > 0:
            return list_of_new_tasks