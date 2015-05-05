"""
based on https://bitbucket.org/DBrent/phd/raw/1d1c5444d2ba2ee3918e0dfd5e886eaeeee49eec/visualisation/plot_gantt.py
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import pylab as pylab


def plot_gantt(simulation_result, top_resources, ax):
    #all the tasks which have been performed
    tasks = simulation_result.execution_history

    #different colors are mapped to the 7 most used resources. These are then mapped to the corresponding frequencies
    colors = ['red', 'blue', 'green', 'cyan', 'magenta', 'black', 'yellow']
    color_map = {}
    label_map = {}

    for i in range(0, len(top_resources)):
        color_map[top_resources[i][0]] = colors[i]
        label_map[colors[i]] = top_resources[i][1]
    label_map["white"] = "No dep. in the top 7"

    #inner function hack to ensure that the labels for each color are only added once.
    def get_label(color):
        if label_map[color] is not None:
            ret = label_map[color]
            label_map[color] = None
            return ret
        else:
            return None
    pos = pylab.arange(0.5, len(tasks) * 0.5 + 0.5, 0.5)


    # Plot the data

    for i in range(0, len(tasks)):

        colors_to_use = []  # stores the colors which correspond to the frequently used hardware
        for resource in tasks[i].usedResources:
            if resource in color_map:
                colors_to_use.append(color_map[resource])

        start_date, end_date = tasks[i].started, tasks[i].finished
        if len(colors_to_use) > 0:
            duration = end_date - start_date
            width = duration / len(colors_to_use)
            current_start = start_date
            for color in colors_to_use:
                ax.barh((i*0.5)+1.0, width, left=current_start, height=0.3, align='center', label=get_label(color),
                        color=color)
                current_start += width
        else:
            ax.barh((i*0.5)+1.0, end_date - start_date, left=start_date, height=0.3, align='center',
                    label=get_label("white"), color='white')

    # Format the y-axis
    locs_y, labels_y = pylab.yticks(pos, map(str, range(0, len(tasks))))
    plt.setp(labels_y, size='medium')

    # Format the x-axis
    ax.axis('tight')

    labels_x =ax.get_xticklabels()
    plt.setp(labels_x, rotation=30, fontsize=10)

    # Format the legend
    font = font_manager.FontProperties(size='small')
    ax.legend(loc=4, prop=font)

    pylab.xlim([0.01, tasks[-1].finished])





