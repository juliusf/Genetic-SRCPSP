__author__ = 'jules'

import argparse
import sys
from deepThought.util import Logger
from deepThought.simulator.simulationResult import load_simulation_result
from deepThought.visualizer.gantt import plot_gantt
import matplotlib.pyplot as plt


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help="The pickle file containing the simulation result")
    arg_parser.add_argument("--pdf", help="specifies that the visualization should be written to a pdf file. Followed \
                            by a path")
    args = arg_parser.parse_args()
    try:
        simulation_result = load_simulation_result(args.file)
    except IOError:
        Logger.error("The file specified was not found.")
        sys.exit(127)
    visualize(simulation_result)

    if args.pdf is not None:
        plt.savefig(args.pdf)
    else:
        plt.show()


def visualize(simulation_result):
    resource_frequency = {}
    for task in simulation_result.execution_history:
        if task.finished - task.started == 0:
            continue
        for resource in task.usedResources:
            if resource.max_share_count is not 0:
                if not resource in resource_frequency:
                    resource_frequency[resource] = 0
                resource_frequency[resource] += 1
    top_resources = []
    for resource, frequency in resource_frequency.items():
        top_resources.append((resource, frequency))

    top_resources.sort(key=lambda tup: tup[1], reverse=True)
    Logger.info("Top required Resources:")

    for resource in top_resources[:10]:
        Logger.info("name: '%s', is testbed: %s, frequency: %s" % (resource[0].name, resource[0].is_testbed, resource[1]))

    fig = plt.figure(figsize=(30, 25))

    ax1 = fig.add_subplot(211)
    plot_gantt(simulation_result, top_resources[:7], ax1)

    ax2 = fig.add_subplot(212)
    plot_gantt(simulation_result, top_resources[:7], ax2)
    ax2.set_xscale('log')

    return ax1, ax2

if __name__ == "__main__":
    main()