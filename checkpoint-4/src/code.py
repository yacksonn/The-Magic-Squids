from collections import Counter
from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import os

def pretty_print(p, last=['']):
	print((' ' * len(last[0].__repr__())), end='\r', flush=True)
	last[0] = p
	print(p, end='\r', flush=True)


def nodes_with_degree(graph, degree):
	return [node for node in graph.nodes if graph.degree[node] <= degree]

def nodes_and_edges(data):
	nodes = set(data['officer_id'].to_list())
	crids = set(data['crid'].to_list())
	edges = []
	for crid in crids:
		officers = set(data[data['crid'] == crid]['officer_id'].to_list())
		crid_edges = combinations(officers, 2)
		for edge in crid_edges:
			edges.append(edge)

	return nodes, edges


def get_graph(data, remove_degrees=-1):
	nodes, edges = nodes_and_edges(data)
	graph = nx.Graph()
	graph.add_nodes_from(nodes)
	graph.add_edges_from(edges)
	graph.remove_nodes_from(nodes_with_degree(graph, remove_degrees))

	return graph


def average_degree(graph):
	degrees = [graph.degree[node] for node in graph.nodes]
	return round(sum(degrees) / len(degrees), 2)


def main():

	os.chdir('..')
	data = pd.read_csv('./data/allegation.csv')

	data = data[data['race'] == "White"]

	G = get_graph(data)
	pretty_print(f'{len(G.edges)} edges between {len(G.nodes)} officers. Average clustering {nx.algorithms.average_clustering(G)}\n\n')

	draw = False
	if draw:
		pretty_print('drawing')
		nx.draw(G, with_labels=True, font_weight='bold')
	
		pretty_print('showing')
		plt.show()



if __name__ == '__main__':
	main()