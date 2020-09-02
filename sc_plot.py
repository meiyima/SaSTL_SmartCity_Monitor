'''
Meiyi Ma, Timothy Davison, Eli Lifland
9/11/18
Two methods for plotting a SC graph using the library geoplotlib.
Includes a sample plot.
'''
import osmnx as ox
import pandas as pd
import geoplotlib
import random
import matplotlib.pyplot as plt
from collections import defaultdict

'''
Loads in nodes according to their coordinates, edges connecting those coordinates
    to a pandas dataframe. That dataframe is passed to/ plotted with geoplotlib.
    Green is used to represent nodes (using the tf_satisfied attribute of the node)
    which are satisfied, and red to represent those unsatisfied.
'''
def plot(graph,tag_to_color,directed=True): 
    color_to_nodes_data = defaultdict(list)
    color_to_nodes_pois = defaultdict(list)
    plot_edges = list()
    for node in graph.nodes: 
        node_info = {'lon':node.coordinates[1], 'lat':node.coordinates[0]}
        color = (0,0,0)
        if len(node.tags):
            if node.tags[0] in tag_to_color:
                color = tag_to_color[node.tags[0]]
            else:
                continue
        if node.data_node:
            color_to_nodes_data[color].append(node_info)
        else:
            color_to_nodes_pois[color].append(node_info)
        neighbors = node.successors
        if not directed:
            neighbors = neighbors.union(node.predecessors)
        for successor in neighbors:
            #if node.coordinates[1] == successor.coordinates[1] and node.coordinates[0] == successor.coordinates[0]:
             #   print(node)
             #   print(successor)
            plot_edges.append({'start_lon':node.coordinates[1], 'end_lon':successor.coordinates[1],
                               'start_lat':node.coordinates[0], 'end_lat':successor.coordinates[0]})
    
    df_edges = pd.DataFrame(plot_edges)
    ''' 
    if not df_edges.empty: 
        geoplotlib.graph(df_edges,
                        src_lat='start_lat',
                        src_lon='start_lon',
                        dest_lat='end_lat',
                        dest_lon='end_lon',
                        color='Dark2',
                        alpha=30,
                        linewidth=3)
    '''
    for color, nodes_list in color_to_nodes_pois.items():
        nodes_df = pd.DataFrame(nodes_list)
        color = list(color)
        color.append(255)
        geoplotlib.dot(nodes_df,color=color)
   
    for color, nodes_list in color_to_nodes_data.items():
        nodes_df = pd.DataFrame(nodes_list)
        color = list(color)
        color.append(255)
        geoplotlib.dot(nodes_df,color=color)

    geoplotlib.show()

def plot_param(city,day,param):
    df = pd.read_csv('data/{c}/{d}/{p}'.format(c=city,d=day,p=param),index_col=0)
    node_id = df.columns[1]
    plt.title('{p} on {d}'.format(p=param,d=day))
    plt.plot(df.index,df[node_id])
    plt.show()

