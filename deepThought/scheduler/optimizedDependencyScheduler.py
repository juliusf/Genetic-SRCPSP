__author__ = 'jules'

from deepThought.scheduler.referenceScheduler import ReferenceScheduler

class OptimizedDependencyScheduler(ReferenceScheduler):
    def __init__(self, job):
        ReferenceScheduler.__init__(self, job)
        self.tasks_to_do = sorted(job.tasks.values(), key=lambda x: x.priority * len(x.required_resources), reverse=True)