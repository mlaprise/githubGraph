#!/usr/bin/env python
# *********************************************
#	
#	Visualize the social the social network
#   of a GitHub user
#
#
#
#	Author: 	Martin Laprise
#		    	Universite Laval
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


def getUserData(userID):
	'''
	Retrieve the social graph info from the user
	'''
	followingList = github.users.following(userID)
	followersList = github.users.followers(userID)

	return [followingList, followersList]


def addUserToGraph(Graph, userID):
	'''
	Add the user to the digraph
	'''	
	[followingList, followersList] = getUserData(userID)

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



# Some Parameters
useScreenName = False
Depth = 2
github = Github(username='YOURUSERNAME',
			    api_token='YOURAPITOKEN')

# List of users to graph
myName = 'mlaprise'
myID = 'mlaprise'
[followingList, followersList] = getUserData(myID)


# Graph creation
githubGraph = digraph()
githubGraph.add_node(myID)
addUserToGraph(githubGraph, myID)


# Graph traversal
for d in range(Depth):
	retrievalItr = traversal(githubGraph, myID, 'post')
	try:
		while 1:
			userID=retrievalItr.next()
			'''
			Add a user to the graph
			Waiting 60 sec if we go beyond the API limitation (60 requests/min)
			'''
			try:
				addUserToGraph(githubGraph, userID)
			except RuntimeError:
				time.sleep(60)
				addUserToGraph(githubGraph, userID)
	except StopIteration:
		print 'Depth ' + str(d+1) + ' Done !'


# Construct the image of the graph
dot = write(githubGraph)
githubGraphViz = AGraph(string=dot)
githubGraphViz.graph_attr['label']='Twitter Graph of ' + myName
githubGraphViz.graph_attr['dpi'] = '2'
githubGraphViz.graph_attr['overlap'] = 'scale'
githubGraphViz.node_attr['label']= ''
githubGraphViz.node_attr['color']= 'blue'
githubGraphViz.node_attr['style']= 'filled'
githubGraphViz.edge_attr['color']='black'
githubGraphViz.layout()

# Draw as PNG
githubGraphViz.draw(myName + '_graph.svg')


