#!/usr/bin/env python

from pylab import *  # for plotting

import graph_tool.all as gt
from ORM.ORM import *


import matplotlib.pyplot as plt

def main():

    data = load_test_data("../../data/testDefinitions.sqlite")
    lengths = []
    g = gt.Graph(directed=False)
    vertices = {}

    for test in data.tests.values():
        vertices[test.id] = g.add_vertex()

    for equipment in data.test_equipment.values():
        all_items = []
        for test in data.tests.values():
            if equipment in test.testEquipment:
                all_items.append(test)
        if len(all_items) > 0:
            lengths.append(len(all_items))
        if len(all_items) > 1:

            for i in range(0, len(all_items)-1):
                for j in range(i, len(all_items)-1):
                    if i != j:
                        g.add_edge(vertices[all_items[i].id], vertices[all_items[j].id])

    pos = gt.arf_layout(g, max_iter=4)
    deg = g.degree_property_map("total")
    gt.graph_draw(g, pos=pos,  vertex_fill_color=deg, vorder=deg, vertex_text=deg, output_size=(800, 600), output="test-testEquipment.png")
    plt.hist(lengths)
    plt.title("Equipment-Test Histogram")
    plt.xlabel("Equipment required by X tests.")
    plt.ylabel("Frequency")
    plt.show()

if __name__ == "__main__":
    main()
