import abc
import copy
import deepThought.ORM.ORM as ORM
from deepThought.util import Logger
__author__ = 'jules'


class Scheduler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, job):
        self.job = job
        self.resource_pool = job.resources
        self.tasks_to_do = {}
        list_of_tasks = sorted(job.tasks.values(), key=lambda x: x.priority, reverse=True) # sort tasks by priority
        for task in list_of_tasks:
            self.tasks_to_do[task.id] = task
        self.task_buffer = []
        self.currently_running_tasks = []
        self.currently_assigned_resoruces = []
        self.execution_history = []
        self.tasks_to_do_unmodified = copy.copy(self.tasks_to_do)
        self.no_resource_conflicts = 0
        self.no_tasks_executed = 0
    def has_next(self):
        if len(self.task_buffer) > 0:  # as long as there are entries in the task buffer, return true
            return True

        tasks = self._reschedule()  # if there are none left, try rescheduling
        if tasks is not None:
            self.task_buffer.extend(tasks)

        if len(self.task_buffer) > 0:
            return True
        else:
            return False  # looks like we're currently out of resources

    def get_next(self):
        assert len(self.task_buffer) > 0, "Don't call get_next() when the task_buffer is empty!"
        task = self.task_buffer.pop(0)
        self.currently_running_tasks.append(task)
        self.no_tasks_executed +=1
        return task

    def get_execution_history(self):
        return self.execution_history

    def has_work_left(self):
        return len(self.tasks_to_do) > 0

    def initialize(self):
        for task in self.tasks_to_do.values():
            for requirement in task.required_resources:
                if not isinstance(requirement, ORM.Resource): # not a specific resource, but a generic one
                    for resource in self.resource_pool.values():
                        if _resources_matches_requirement_slow(requirement, resource):
                            requirement.fulfilled_by.append(resource.id)
                else:
                    requirement.required_by.append(task)

    def get_tasks_eligible_to_run(self):
        eligible_to_run = []
        for task in self.tasks_to_do.values():
            if self._is_eligible_to_run(task):
                eligible_to_run.append(task)
        return eligible_to_run

    def get_task_ids_eligible_to_run(self):
        tasks = self.get_tasks_eligible_to_run()
        ids = []
        for task in tasks:
            ids.append(task.id)
        return ids

    def _is_eligible_to_run(self, task):
        scheduled_task = ScheduledTask(task, self)
        temp_reserved_resources = []

        test_bed = _find_test_bed(task)

        for resource in scheduled_task.required_resources:
            if isinstance(resource, ORM.Resource):
                if resource.id in self.resource_pool:
                    self._temp_allocate(temp_reserved_resources, resource)
                else:  # the fix assigned equipment is not available. we can return directly
                    self._cleanup_failed_allocation(temp_reserved_resources)
                    return False

        # do this in two passes in order to avoid premature allocation of fixed devices
        for resource in scheduled_task.required_resources:
            if isinstance(resource, ORM.RequiredResource):
                    assigned_resource = self._map_requirement_to_available_resource(resource, test_bed)
                    if assigned_resource is None:
                        self._cleanup_failed_allocation(temp_reserved_resources)
                        return False
                    self._temp_allocate(temp_reserved_resources, assigned_resource)

        self._cleanup_failed_allocation(temp_reserved_resources)
        return True

    def allocate_resources(self, task):

        scheduled_task = ScheduledTask(task, self)
        temp_reserved_resources = []

        test_bed =  _find_test_bed(task)

        for resource in scheduled_task.required_resources:
            if isinstance(resource, ORM.Resource):
                if resource.id in self.resource_pool:
                    self._temp_allocate(temp_reserved_resources, resource)
                else:  # the fix assigned equipment is not available. we can return directly
                    self.no_resource_conflicts +=1
                    return self._cleanup_failed_allocation(temp_reserved_resources)

        # do this in two passes in order to avoid premature allocation of fixed devices
        for resource in scheduled_task.required_resources:
            if isinstance(resource, ORM.RequiredResource):
                    assigned_resource = self._map_requirement_to_available_resource(resource, test_bed)
                    if assigned_resource is None:
                        self.no_resource_conflicts +=1
                        return self._cleanup_failed_allocation(temp_reserved_resources)
                    self._temp_allocate(temp_reserved_resources, assigned_resource)

        scheduled_task.usedResources = temp_reserved_resources
        self.currently_assigned_resoruces.extend(temp_reserved_resources)
        return scheduled_task

    def _map_requirement_to_available_resource(self, required, test_bed):
        list_of_matching_resource_ids = list(set(required.fulfilled_by) & set(self.resource_pool.keys()))
        if len(list_of_matching_resource_ids)  == 0: #no resource available
            return None

        resources = []
        for resource_id in list_of_matching_resource_ids: #heuristic: use the resource which produces the least overlap.
            resource = self.resource_pool[resource_id] #get the resource via the id
            resources.append( (len(resource.provided_capabilities), resource))
        resource = sorted(resources, key=lambda res: res[0])[0][1]

        return resource

    def _cleanup_failed_allocation(self, already_allocated):
        for allocation in already_allocated:
            if allocation.max_share_count == 0:
                continue
            if allocation.share_count == 0:
                self.resource_pool[allocation.id] = allocation
            allocation.share_count += 1
        return None

    def _temp_allocate(self, temp_allocation_pool, resource):
        temp_allocation_pool.append(resource)
        if resource.max_share_count == 0:
            return
        resource.share_count -= 1
        if resource.share_count == 0:
            del self.resource_pool[resource.id]
    def reset_schedule(self):
            self.tasks_to_do = copy.copy(self.tasks_to_do_unmodified)

def _resources_matches_requirement_slow(requirement, resource):
    for required in requirement.required_capabilities:
        fulfilled = False
        for provided in resource.provided_capabilities:
            if _compare_capabilities(required, provided):
                fulfilled = True
                break
        if not fulfilled:
            return False
    return True

def _map_requirement_to_available_resource(self, required, test_bed):
        list_of_matching_resources = list(set(required.fulfilled_by) & set(self.resource_pool.keys()))
        if len(list_of_matching_resources)  == 0:
            return None
        return self.resource_pool[list_of_matching_resources[0]]

def _compare_capabilities(required, provided):
    return provided.id == required.id

def _find_test_bed(task):
    for requirement in task.required_resources:
        if requirement.is_testbed is True:
            return requirement
    return None





class ScheduledTask(ORM.Task):
    def __init__(self, task, scheduler):
        #ORM.Task.__init__(self)
        #self.original_task = task
        self.__dict__ = copy.copy(task.__dict__)  # Copys all values from the task to the current object
        self.original_task = task
        self.usedResources = []
        self.scheduler = scheduler
        self.started = 0
        self.finished = 0
        self.duration = 0
    # callback for marking a Task as completed. This is used to return bound resources to the pool.

    def set_completed(self):
        self.scheduler.currently_running_tasks.remove(self)
        for resource in self.usedResources:
            self.scheduler.currently_assigned_resoruces.remove(resource)
            if resource.max_share_count == 0:
                continue
            if resource.share_count == 0:
                self.scheduler.resource_pool[resource.id] = resource
            resource.share_count += 1
            self.scheduler.resource_pool[resource.id] = resource

        self.scheduler.execution_history.append(self)

    def set_started(self, now):
        self.started = now

    def set_finished(self, now):
        self.finished = now
        self.duration = self.finished - self.started

    @abc.abstractmethod
    def _reschedule(self):
        return None
