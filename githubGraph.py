#!/usr/bin/env python
# *********************************************
#	
#	Visualize the social the social network
#	of a GitHub user
#
#
#
#	Author:		Martin Laprise
#		   		Universite Laval
#				martin.laprise.1@ulaval.ca
#                 
# *********************************************


import time

# Import pygraph
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms.traversal import traversal
from pygraph.readwrite.dot import write


# Import pygraphviz
from pygraphviz import *


# Import github2 api client
from github2.client import Github


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
		Add the user to the digraph
		'''	
		[followingList, followersList] = self.getUserData(userID)

		for snUser in followingList:
			if (snUser not in Graph.nodes()) and (snUser in followersList):
				Graph.add_node(snUser)
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
						except (RuntimeError, gaierror):
							time.sleep(60)
							self.addUserToGraph(githubGraph, userID)
				except StopIteration:
					print 'Depth ' + str(d+1) + ' Done !'


			return githubGraph
			

	def pngViz(self, graph, filename, pngDPI = 10):
		# Construct the image of the graph
		dot = write(graph)

		githubGraphViz = AGraph(string=dot)
		githubGraphViz.graph_attr['label']='Twitter Graph of ' + str(graph)
		githubGraphViz.graph_attr['dpi'] = str(pngDPI)
		githubGraphViz.graph_attr['overlap'] = 'scale'
		githubGraphViz.node_attr['label']= ''
		githubGraphViz.node_attr['color']= 'blue'
		githubGraphViz.node_attr['style']= 'filled'
		githubGraphViz.edge_attr['color']='black'
		githubGraphViz.edge_attr['penwidth']='5'
		githubGraphViz.layout()

		# Draw as PNG
		githubGraphViz.draw(filename + '.png')


	def dotViz(self, graph):
		# Construct the image of the graph
		dot = write(graph)

		# Write a dot file
		myfile = file(filename + '.dot', 'w')
		myfile.write(dot)



