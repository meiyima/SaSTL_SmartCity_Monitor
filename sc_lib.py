'''
Meiyi Ma, Timothy Davison, Eli Lifland
STL for Smart Cities
Object Library: Node, Edge, Graph
'''
import queue
import pandas as pd
import numpy as np
import osmnx as ox
from collections import defaultdict
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry import MultiPoint
import geopy

class node:
    def __init__(self, ID, coordinates):
        if isinstance(ID,list):
            ID = tuple(sorted(ID))
        self.ID = str(ID)
        self.coordinates = coordinates #(lat,lon)
        self.tf_satisfied = True # whether req is satisfied
        self.tags = list()
        self.predecessors = set()
        self.successors = set()
        self.intersections = tuple()
        self.data_node = True
        self.loc_dict = dict()

    #returns distance between self and other in km
    def dist_to(self,other):
        return geopy.distance.vincenty(self.coordinates,other.coordinates).km

    def __str__(self):
        ret = 'ID: {} Coordinates: {}'.format(self.ID,self.coordinates)
        ret += '\ntags: {}'.format(self.tags)
        return ret

    def add_successor(self, node):
        self.successors.add(node)
        
    def add_predecessor(self, node):
        self.predecessors.add(node)

    def add_tag(self,tag):
        self.tags.append(tag)

    def set_df(self,df):
        self.df = df

    #for sets
    def __eq__(self,other):
        return self.ID == other.ID and self.coordinates == other.coordinates

    def __hash__(self):
        return hash(self.ID) ^ hash(self.coordinates)
   
class edge:
    def __init__(self, ID, coordinates):
        if isinstance(ID,list):
            ID = tuple(sorted(ID))
        self.ID = ID
        self.coordinates = coordinates    

    #for sets
    def __eq__(self,other):
        return self.ID == other.ID and self.coordinates == other.coordinates

    def __hash__(self):
        return hash(self.ID) ^ hash(self.coordinates)
    
class graph:
    def __init__(self):
        self.nodes_by_ID = dict()
        self.nodes = set()
        self.data_nodes = set()
        self.edges = set()
        self.edge_dict = dict()
        self.test = 1

    def add_sensor_locs(self,sensor_path):
        sensor_df = pd.read_csv(sensor_path)
        for index, row in sensor_df.iterrows():
            p = (row['lat'],row['lon'])
            new_node = node(row['node_id'],p)
            self.add_node(new_node)

    def add_edge(self,edge):
        if edge not in self.edges:
            self.edges.add(edge)
            self.edge_dict[edge.ID] = edge
            return True
        return False

    def add_node(self,node):
        if node not in self.nodes:
            self.nodes_by_ID[node.ID] = node
            self.nodes.add(node)
            if node.data_node:
                self.data_nodes.add(node)
            return True
        return False

    def get_nodes_with_tag(self,tag):
        return [node for node in self.nodes if tag in node.tags]

    def a_node(self):
        return next(iter(self.nodes))

    def add_node_with_tag(self,ID,loc,tag):
        new_node = node(ID,loc)
        new_node.add_tag(tag)
        new_node.data_node=False
        self.add_node(new_node)

    #add OSM points of interest to graph within distance dist of point p
    def add_OSMnx_pois(self,amenities=None,p=None,dist=2500,north=None,south=None,east=None,west=None):
        nearby_pois = None
        if p:
            nearby_pois = ox.pois_from_point(p,distance=dist,amenities=amenities)
        else:
            nearby_pois = ox.osm_poi_download(north=north,south=south,east=east,west=west,amenities=amenities)
        for index, row in nearby_pois.iterrows():
            if not isinstance(row['amenity'],str):
                continue
            geo = row['geometry']
            point = (0,0)
            try:
                point = (geo.y,geo.x)
            except:
                point = (geo.centroid.y,geo.centroid.x)
            new_node = node(row['osmid'],point)
            new_node.add_tag(row['amenity'])
            new_node.data_node = False
            self.add_node(new_node)

    def add_chi_parks(self):
        parks = [(41.882419,-87.619292),(41.886293,-87.717201),(41.882591,-87.622543),(41.835649,-87.607340),(41.874336,-87.769523),(41.872181,-87.618754),(41.854334,-87.653914),(41.920975,-87.645624),(41.868139,-87.629830),(41.870542,-87.654764),(41.811451,-87.634616),(41.943953,-87.738916),(41.906938,-87.702270),(41.850048,-87.716968),(41.930524,-87.653400),(41.886097,-87.617916),(41.922837,-87.634413),(41.833970,-87.634935),(41.913902,-87.668320),(41.811520,-87.719006),(41.888146,-87.761837),(41.936619,-87.679609),(41.879856,-87.650227),(41.921880,-87.685120),(41.906436,-87.663423),(41.840795,-87.647557),(41.905948,-87.645240),(41.856888,-87.673073),(41.874406,-87.692707),(41.916247,-87.641779),(41.814034,-87.610283)]
        id_str = 'park'
        c = 0
        for p in parks:
            new_node = node('{}{}'.format(id_str,str(c)),p)
            new_node.add_tag('park')
            new_node.data_node = False
            self.add_node(new_node)
            c+=1

    def add_ny_parks(self):
        parks = [(40.784824,-73.965903),(40.765240,-73.958713),(40.801295,-73.972345),(40.760251,-73.975106),(40.768086,-73.994618),(40.777342,-73.982367),(40.773303,-73.968259),(40.779770,-73.970086),(40.766644,-73.975022),(40.775736,-73.975209),(40.778637,-73.984325),(40.771252,-73.995550),(40.764729,-73.973146),(40.781333,-73.986585),(40.753613,-73.983263),(40.770596,-73.995385),(40.779148,-73.981707),(40.772761,-73.976725),(40.774620,-73.988897),(40.781854,-73.974764),(40.747996,-74.004763),(40.777764,-73.969649),(40.773590,-73.982022),(40.781621,-73.963474),(40.780961,-73.950144),(40.776355,-73.965660),(40.772302,-73.986238),(40.769302,-73.949400),(40.769277,-73.975923),(40.801838,-73.968299),(40.730800,-73.997281),(40.850895,-73.945106),(40.714990,-73.989360),(40.738186,-74.010887),(40.735789,-73.990518),(40.741978,-73.987600),(40.717060,-74.015495),(40.721134,-74.013151),(40.852798,-73.938056),(40.703258,-74.017065),(40.793248,-73.955440)]
        id_str = 'park'
        c = 0
        for p in parks:
            new_node = node('{}{}'.format(id_str,str(c)),p)
            new_node.add_tag('park')
            new_node.data_node = False
            self.add_node(new_node)
            c+=1
            
    def add_chi_high_crime(self):
        df = pd.read_csv('crime_data.csv')
        id_str = 'crime'
        c = 0
        for index,row in df.iterrows():
            new_node = node('{}{}'.format(id_str,str(c)),(row['latitude'],row['longtitude']))
            new_node.add_tag('high_crime')
            new_node.data_node = False
            self.add_node(new_node)
            c+=1

    #add OSM nodes within distance dist of p, assign data to them 
    def add_OSMnx_data_within_dist(self,p,dist=250,data_id=None,data_df=None):
        try:
            osmnx_graph = ox.graph_from_point(p,distance=dist,network_type='drive')
        except:
            return
        node_data = osmnx_graph.node.data()

        for item in node_data:
            new_edge = edge(item[0],(item[1]["y"],item[1]["x"]))
            self.add_edge(new_edge)
        
        edge_data = osmnx_graph.edges(data=True)

        intersection_to_nodes = defaultdict(list)
        for item in edge_data:       
            intersection0Coords = self.edge_dict[item[0]].coordinates 
            intersection1Coords = self.edge_dict[item[1]].coordinates 
            lon = (intersection0Coords[1] + intersection1Coords[1])/2.0
            lat = (intersection0Coords[0] + intersection1Coords[0])/2.0
            
            new_node = node(item[2]['osmid'], (lat,lon))
            new_node.intersections = (item[0], item[1])      
            new_node.data_id = data_id
            new_node.df = data_df
            if self.add_node(new_node):
                intersection_to_nodes[new_node.intersections[0]].append(new_node)
    
        for node_a in self.nodes:
            if not node_a.intersections:
                continue
            for node_b in intersection_to_nodes[node_a.intersections[1]]:
                node_a.add_successor(node_b)
                node_b.add_predecessor(node_a)

    def centroid(self):
        lat_sum = 0
        lon_sum = 0
        for node in self.nodes:
            lat_sum += node.coordinates[0]
            lon_sum += node.coordinates[1]
        return (lat_sum/len(self.nodes),lon_sum/len(self.nodes))

class requirement():
    def __init__(self):
        self.req_str = ''
        self.pretty_str = ''

    def set_req_str(self,s):
        self.req_str = s

    def set_pretty_str(self,s):
        self.pretty_str = s

    def construct_req_str(self,agg,param,rang,spatial,label,temporal,rel,val,fro,to):
        self.req_str = ''
        if spatial == '<all/everywhere>':
            self.req_str += 'W'
        else:
            self.req_str += 'S'
        if len(label):
            self.req_str += '{'+label[1:-2]+'}'
        self.req_str += '('
        if temporal == '<always>':
            self.req_str += 'A'
        else:
            self.req_str += 'E'
        self.req_str += '[{},{}]'.format(fro,to)
        if len(agg):
            self.req_str += '(<{}[{},{}],{}>'.format(agg[1:-1],0,rang,param[1:-1])
        else: 
            self.req_str += '(<{}>'.format(param[1:-1]) 
        if rel == '<above>': 
            self.req_str += '({},inf)))'.format(val)
        elif rel == '<below>':
            self.req_str += '(-inf,{})))'.format(val)
        self.pretty_str = 'The '
        if len(agg):
            self.pretty_str += agg+' '
        self.pretty_str += param+' '
        my_spatial = spatial.split('/')[0]+'>' if len(label) else '<'+spatial.split('/')[1]
        if len(label):
            self.pretty_str += 'within <{}> km of {} {} '.format(rang,my_spatial,label)
        else:
            self.pretty_str += my_spatial+' '
        self.pretty_str += 'should {} be {} <{}> from minute <{}> to minute <{}>'.format(temporal,rel,val,fro,to)


