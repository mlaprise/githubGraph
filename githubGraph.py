#!/usr/bin/env python

"""

Visualize the social network of a GitHub user

Copyright (C) 2007-2010 Martin Laprise (mlaprise@gmail.com)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 dated June, 1991.

This software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA


"""


import time

# Import pygraph
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms.traversal import traversal
from pygraph.readwrite.dot import write
from pygraph.readwrite.dot import read


# Import pygraphviz
from pygraphviz import *


# Import github2 api client
from github2.client import Github

# Import the ubigraph server stuff
import xmlrpclib
import time

class githubGraph:

	def __init__(self, userName, apiToken):
		self.ghConnect = Github(username=userName, api_token=apiToken)

	def getUserData(self, userID):
		'''
		Retrieve the social graph info from the user
		'''
		followingList = self.ghConnect.users.following(userID)
		followersList = self.ghConnect.users.followers(userID)

		return [followingList, followersList]


	def addUserToDigraph(self, Graph, userID):
		'''
		Add the user to the digraph
		'''	
		[followingList, followersList] = self.getUserData(userID)

		for snUser in followingList:
			if snUser not in Graph.nodes():
				Graph.add_node(snUser)
			if (userID, snUser) not in Graph.edges():
				Graph.add_edge([userID, snUser])

		for snUser in followersList:
			if snUser not in Graph.nodes():
				Graph.add_node(snUser)
			if (snUser, userID) not in Graph.edges():
				Graph.add_edge([snUser, userID])
		print str(len(Graph)) + ' nodes'



	def addUserToGraph(self, Graph, userID):
		'''
		Add the user to the graph
		'''	
		[followingList, followersList] = self.getUserData(userID)

		for snUser in followingList:
			if (snUser not in Graph.nodes()) and (snUser in followersList):
				Graph.add_node(snUser)
			if (userID, snUser) not in Graph.edges() and (snUser in followersList):			
				Graph.add_edge([userID, snUser])

		print str(len(Graph)) + ' nodes'



	def ffDigraph(self, myID, depth = 1, pngOutput = 1, dotOutput = 1, pngDPI = 10):
		'''
		Generate the following/followers digraph
		'''	
	
		myName = myID

		[followingList, followersList] = self.getUserData(myID)


		# Graph creation
		githubGraph = digraph()
		githubGraph.add_node(myID)
		self.addUserToDigraph(githubGraph, myID)


		# Graph traversal
		for d in range(depth):
			retrievalItr = traversal(githubGraph, myID, 'post')
			try:
				while 1:
					userID=retrievalItr.next()
					'''
					Add a user to the graph
					Waiting 60 sec if we go beyond the API limitation (60 requests/min)
					'''
					try:
						self.addUserToDigraph(githubGraph, userID)
					except RuntimeError:
						time.sleep(60)
						self.addUserToDigraph(githubGraph, userID)
			except StopIteration:
				print 'Depth ' + str(d+1) + ' Done !'


		return githubGraph


	def ffGraph(self, myID, depth = 1):
			'''
			Generate the following/followers graph, only add an edge if the two
			users follow each other.
			'''	
	
			myName = myID

			[followingList, followersList] = self.getUserData(myID)


			# Graph creation
			githubGraph = graph()
			githubGraph.add_node(myID)
			self.addUserToGraph(githubGraph, myID)


			# Graph traversal
			for d in range(depth):
				retrievalItr = traversal(githubGraph, myID, 'post')
				try:
					while 1:
						userID=retrievalItr.next()
						'''
						Add a user to the graph
						Waiting 60 sec if we go beyond the API limitation (60 requests/min)
						'''
						try:
							self.addUserToGraph(githubGraph, userID)
						except RuntimeError, gaierror:
							time.sleep(60)
							self.addUserToGraph(githubGraph, userID)
				except StopIteration:
					print 'Depth ' + str(d+1) + ' Done !'


			return githubGraph


	def pngViz(self, graph, filename, pngDPI = 10, penwidth = 5):
		# Construct the image of the graph
		dot = write(graph)

		githubGraphViz = AGraph(string=dot)
		githubGraphViz.graph_attr['label']='Social Graph of ' + str(graph)
		githubGraphViz.graph_attr['dpi'] = str(pngDPI)
		githubGraphViz.graph_attr['overlap'] = 'scale'
		githubGraphViz.node_attr['label']= ''
		githubGraphViz.node_attr['color']= 'blue'	
		githubGraphViz.node_attr['style']= 'filled'
		githubGraphViz.node_attr['shape']='circle'
		githubGraphViz.edge_attr['color']='black'
		githubGraphViz.edge_attr['penwidth']='10'
		githubGraphViz.layout()

		# Draw as PNG
		githubGraphViz.draw(filename + '.png')

	
	def ubiServer(self, graph, label=[]):
		'''
		Dynamicaly visualizing the graph using the ubigraph server
		(force-directed layout algorithm)
		'''

		server_url = 'http://127.0.0.1:20738/RPC2'
		server = xmlrpclib.Server(server_url)
		G = server.ubigraph;
		G.clear()
		#G.set_edge_style_attribute(0, "spline", "true")
		
		# List of nodes
		nodes = graph.nodes()
		# List of edges
		edges = graph.edges()
		# Dict mapping the name of the nodes with the id returned by the server
		nodes_id = {}
		
		# Add all the nodes to the server
		for node in nodes:
			node_id = G.new_vertex()
			nodes_id[node] = node_id
			if node in label:
				G.set_vertex_attribute(node_id, "label", node)
				G.set_vertex_attribute(node_id, 'color', '#ffff40')
				G.set_vertex_attribute(node_id, 'size', '5.0')			

		# Add all the edges to the server
		for edge in edges:
			 G.new_edge(nodes_id[edge[0]], nodes_id[edge[1]])

		
	def dotViz(self, graph, filename):
		# Construct the image of the graph
		dot = write(graph)

		# Write a dot file
		myfile = file(filename + '.dot', 'w')
		myfile.write(dot)



