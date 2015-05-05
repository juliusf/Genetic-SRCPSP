#!/usr/bin/env python

import sqlite3

import graph_tool.all as gt

def main():

    conn = sqlite3.connect('../../data/testDefinitions.sqlite')
    g = gt.Graph()
    cursor = conn.cursor()
    cursor.execute('select id, testBed from tests;')
    tests = {}
    ids = []
    for entry in cursor.fetchall():
        tests[entry[0]] = g.add_vertex()

    cursor.execute('select id from testBeds;')

    for entry in cursor.fetchall():
        ids.append(entry[0])

    for id in ids:
        cursor.execute("select tests.id from tests where testBed = '{}'".format(id))

        all_items = cursor.fetchall()
        if len(all_items)  > 1:
            for i in range(0, len(all_items)-1):
                for j in range(i +1, len(all_items)):
                    g.add_edge(tests[all_items[i][0]], tests[all_items[j][0]])

    #g = gt.GraphView(g, vfilt=gt.label_largest_component(g))
    kcore = gt.kcore_decomposition(g)
    #gt.graph_draw(g, vertex_fill_color=kcore, vertex_text=kcore, output="test-testBed.pdf")
    gt.graph_draw(g, vertex_font_size=12, output_size=(800, 600), output="test-testBed.png")

if __name__== "__main__":
    main()
