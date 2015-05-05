import numpy as np


class SimulationEntity(object):
    def __init__(self, env, task, callback, stochastic, old_execution_history):
        self.env = env
        self.task = task
        self.action = env.process(self.run())
        self.callback_proc = callback
        self.stochastic = stochastic
        self.old_execution_history = old_execution_history

    def run(self):

        self.task.set_started(self.env.now)
        yield self.env.timeout(self.compute_sleep_duration())
        self.task.set_finished(self.env.now)
        self.task.set_completed()
        self.callback_proc(self.env)

    def compute_sleep_duration(self):
        if self.old_execution_history is not None:
            duration = self.old_execution_history.jobs[self.task.id].duration
            return duration

        if self.stochastic:
            return self.task.get_next_execution_time()
        else:
            return self.task.mean

