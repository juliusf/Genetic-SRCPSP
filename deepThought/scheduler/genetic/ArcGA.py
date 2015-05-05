__author__ = 'jules'

"""
This algorithm selects further precedence constrains to add to the List of
"""
from deap import tools, base, creator, algorithms
from deepThought.scheduler.RBPolicy import RBPolicy
from deepThought.scheduler.MfssRb import MfssRB
from deepThought.util import Logger, UnfeasibleScheduleException
import random
import copy
import numpy as np


class ArcGA():

    def __init__(self, job, base_schedule):
        import deepThought.simulator.simulator as sim
        self.job = job # this is required for the simulator which is needed to compute the fitness of an individual
        self.base_schedule = base_schedule[:]
        self.toolbox = base.Toolbox()
        self.n_pairs = 7
        self.no_p = 10


        creator.create("FitnessMax", base.Fitness, weights=(1.0,-2.0)) # we want to minimize the makespan
        creator.create("ArcList", list, fitness=creator.FitnessMax)

        #compute t of schedule without arcs:

        #self.base_t = sim.simulate_schedule(schedule, stochastic=False ).total_time

        def create_inital_arc_list():
            tmp_list = []
            for resource in job.resources.values():
                if len(resource.required_by) > 1:
                    for tuple in range(1, random.randrange(1, self.n_pairs)):
                        tuple = (random.choice(resource.required_by).id, random.choice(resource.required_by).id)
                        assert(tuple[0] in self.job.tasks.keys())
                        assert(tuple[1] in self.job.tasks.keys())
                        if tuple[0] == tuple[1]:
                            continue
                        tmp_list.append(tuple)
            tmp_list = random.sample(tmp_list, random.randrange(1, self.no_p))
            return creator.ArcList(tmp_list)

        def create_initial_pop():
            individual = []
            for i in range(self.no_p):
                while True: #This ensures that in the first iteration we don't accidentially draw the same two items
                    individual.append(self.create_new_individual_from_complement(individual))
                    latest = individual[-1]
                    if latest[0] is not latest[1]:
                        break
            return creator.ArcList(individual)

        #The actual fitness function
        def evalSchedule(individual):
            rb_policy_schedule = RBPolicy(self.job, self.base_schedule)
            reference = sim.simulate_schedule(rb_policy_schedule, stochastic=True )

            scheduler = MfssRB(self.job, self.base_schedule, individual)
            try:
                time = sim.simulate_schedule(scheduler, old_execution_history=reference ).total_time
            except UnfeasibleScheduleException:
                return None
            return (reference.total_time - time, scheduler.no_resource_conflicts)

        #self.toolbox.register("population", tools.initRepeat, list, create_inital_arc_list)
        self.toolbox.register("population", tools.initRepeat, list, create_initial_pop)
        self.toolbox.register("evaluate", evalSchedule)
        self.toolbox.register("select", tools.selBest)
        self.toolbox.register("map",  map)

        self.stats = tools.Statistics(key=lambda ind: ind.fitness.values[0] if ind.fitness.valid else -100000)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

        self.logbook = tools.Logbook()

    def do_it(self, ngen, cxpb, mutpb):
        Logger.info("ArcGA: Creating Initial Population")
        pop = self.toolbox.population(n=self.no_p)
        Logger.info("ArcGA: Calculating base fitness")
        #inital calculation of fitness for base population.
        fitness = self.toolbox.map(self.toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitness):
            if fit is not None:
                ind.fitness.values = fit

        best = [copy.deepcopy(ind) for ind in pop]
        for g in range(ngen):

            Logger.info("ArcGA Generation: %s" % (g))
            best = self.select(pop, self.no_p)
            record = self.stats.compile(best)
            self.logbook.record(**record)
            pop = [copy.deepcopy(ind) for ind in best]

            if random.random() < cxpb:
                self.crossover(pop, cxpb)


            for mutant in pop:
               if random.random() < mutpb:
                    self.mutate(mutant, 0.5)


            #invalids = [ind for ind in pop if not ind.fitness.valid]
            for ind in best:
                if not ind in pop:
                    pop.append(ind)

            fitnesses = self.toolbox.map(self.toolbox.evaluate, pop)
            for ind, fit in zip(pop, fitnesses):
                if fit is not None:
                    ind.fitness.values = fit

        best = self.select(pop, n=1)
        return best

    def select(self, pop, n):
        #selection = sorted(pop, key=lambda ind: ind.fitness.values[0] - 100 * ind.fitness.values[1] if ind.fitness.valid else None, reverse=True)[:n]
        selection = sorted(pop, key=lambda ind: ind.fitness.values[0] if ind.fitness.valid else None, reverse=True)[:n]
        # for entry in selection:
        #     if entry.fitness.valid:
        #         print entry.fitness.values
        #     else:
        #         print("invalid")
        return selection

    def create_new_individual_from_complement(self, individual):

        while True:
            new_candidate = (random.choice(self.job.tasks.keys()), random.choice(self.job.tasks.keys()))
            for tuple in individual:
                if new_candidate[0] == tuple[0] and new_candidate[1] == tuple[1] or new_candidate[0] == new_candidate[1]:
                    break
            else:
                return new_candidate



    def crossover(self, population, cxpb):
        to_cross = copy.deepcopy(population)
        offsprings = []
        while len(to_cross) > 1:
            father = random.choice(to_cross)
            mother = random.choice(to_cross)
            #while mother == father:
            #    if len(father) == 0 and len(mother) == 0:
            #         return #nothing to do here.
            #    father = random.choice(to_cross)
            #    mother = random.choice(to_cross)


            to_cross.remove(father)
            if father is not mother:
                to_cross.remove(mother)

            son = creator.ArcList()
            daughter = creator.ArcList()

            for element in father:
                if random.random() < 0.5:
                    son.append(element)
                else:
                    daughter.append(element)

            for element in mother:
                if random.random() < 0.5:
                    son.append(element)
                else:
                    daughter.append(element)

            offsprings.append(son)
            offsprings.append(daughter)
        population.extend(offsprings)

    def mutate(self, to_mutate, pbx):

        if random.random() < 0.5:
            if len(to_mutate) is not 0:
                to_mutate.remove(random.choice(to_mutate))
        else:
            to_mutate.append(self.create_new_individual_from_complement(to_mutate))

    def get_logbook(self):
        return self.logbook

