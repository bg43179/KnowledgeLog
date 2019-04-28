import sys
import json
import requests
from tree import rule_selector
from node import RuleNode, trim
from pyDatalog import pyDatalog
from request import pull_from_fuseki


def cache(response, sub, predicate, obj, predicate_map = {}):
	"""
		Method for pulling data form fuseki, support 4 different requests body

	Args:
		response: json(dict) return from fuseki server
	    subject: subject
	    predicate: predicate
	    obj: object 
	    predicate: Use for checking if the relation(predicate) talbe already exist
	"""
	# first create terms for all the predicates
	count = 0
	# add an instance in this format (+prdicate(subject, object))
	for index, instance in enumerate(response['results']['bindings']):	
		
		current_pred = predicate
		item = {}
		
		for key, value in instance.items():
			
			# create a new relation table if the given predicate is not exist, can be removed in our case
			# if key == predicate:
			# 	if key not in predicate_map:
			# 		pyDatalog.create_terms(value["value"].split(":")[1])
			# 		predicate_map[value["value"].split(":")[1]]= 1
			# 	current_pred = value["value"].split(":")[1]

			if key == sub:
				item[sub] = value["value"].split(":")[1]
				
			if key == obj:
				item[obj] = value["value"].split(":")[1]
		
		# add the fact
		pyDatalog.assert_fact(current_pred, item[sub], item[obj])
		count += 1

	print(count)

def partition_cache(node, predicate_map, no_of_partition=5):
	
	"""
		This method can load all the relation in one rule into memory. 
		Divide all the relation into 5 different partition, each represent different probability
	"""
	table = []

	for predicate in node.raw_set:
		
		predicates = []	
		
		for num in range(no_of_partition):
			name = trim(predicate ,1, "r") + "__prob__" + str(num+1)
			predicates.append(name)
			
			if name not in predicate_map:
				pyDatalog.create_terms(name)
				predicate_map[name] = 1

				if (num+1) == no_of_partition:
				# if data haven't been loaded into DB, add it from fuseki 
					sub, obj= "subject", "object"
					predicate_map[predicates[-1]] = 1

					# TODO: modify the string passed in 
					print(predicate)
					response = pull_from_fuseki(sub, predicate, obj, 2)
					cache(response, sub, predicates[-1], obj, predicate_map)

		table.append(predicates[:])


	# Join two relations(or one relation)
	# for i in range(len(table)):
		# for j in range(len(table[0])):


	# print(table)
	# print(predicate_map)


def partition_loader():
	"""
		Method for loading rule and load data into memory at once(cache)
	"""

	rules, relations = rule_selector("<dbo:author>", 2)
	knowledge(rules)


def loader(): 
	"""
		Method for loading rule and load data into memory at once(cache)
	"""

	# load rule and generate a list of relations
	rules, relations = rule_selector("<dbo:author>", 1)
	predicate_map = {}

	for predicate in relations:
		sub, obj= "subject", "object"

		pred = trim(predicate, 1, "r")
		print(pred)

		if pred not in predicate_map:
			pyDatalog.create_terms(pred)
			predicate_map[pred] = 1

		response = pull_from_fuseki(sub, predicate, obj, 2)
		cache(response, sub, pred, obj, predicate_map)


def knowledge(rules):
	
	predicate_map = {}
	rule_map = {}
	idb_set = set()
	

	# iterate thru all rules and find the idb and edb
	for index, rule in enumerate(rules):
	
		# TODO: fix input

		node = RuleNode(rule[0], rule[1])
		idb_set.add( node.left )

		rule_map[str(index)] = node

	# while rule_map is not empty
	# print("\n".join(n.rule for n in rule_map.values()))

	while rule_map:
		to_remove = set()

		for key in list(rule_map.keys()):
			node = rule_map[key]
			# print(node.right_set)
			if not idb_set.intersection(node.right_set):
				
				partition_cache(node, predicate_map)
				
				to_remove.add(node.left)
				
				del rule_map[key]

		print("Before", idb_set)
						
		idb_set = idb_set.difference(to_remove)
		print("")
		print("\n".join(n.rule for n in rule_map.values()))
		
		print("")
		# print(to_remove)
		print("After", idb_set)
		print("")



if __name__ == "__main__":
	

	# sub, pred, obj= "subject", "predicate", "object"
	# response = pull_from_fuseki(sub, pred, obj, 0);
	# cache(sub, pred, obj)
	
	# loader()
	partition_loader()
	pyDatalog.create_terms("X", "Y", "Z")
	# print(pyDatalog.ask("influenced" + '(X, Y)'))

	# print(pyDatalog.ask('author' + '(X, "George_Orwell")'))

