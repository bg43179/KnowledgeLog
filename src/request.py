import sys
import json
import requests
from tree import rule_selector
from pyDatalog import pyDatalog


class RuleNode():
	def __init__(self, rule):
		
		self.rule = rule

		rule = rule.split("<=")
		right = rule[1].split("&")

		self.right_set = set([self.trim(right[0].strip(), self.trim(right[1])]) if len(right) == 2 else set([self.trim(right[0])])
		self.right = rule[1].strip()
		self.left = self.trim(rule[0])

	def trim(self, string):
		return string.split("(")[0].strip()

def pull_from_fuseki(subject, predicate, obj, option):
	"""
		Method for pulling data form fuseki, support 4 different requests body

	Args:
	    subject: subject
	    predicate: predicate
	    obj: object 
	    option: (0) all unknown (1) s known (2) p known (3) o known

	Returns:
	    return a json 
	"""
	if option == 0:
		body = "SELECT ?{s} ?{p} ?{o} WHERE {{ ?{s} ?{p} ?{o} }}".format(s=subject, p=predicate, o=obj)
	elif option == 1:
		body = "SELECT ?{p} ?{o} WHERE {{ {s} ?{p} ?{o} }}".format(s=subject, p=predicate, o=obj)
	elif option == 2:
		body = "SELECT ?{s} ?{o} WHERE {{ ?{s} {p} ?{o} }}".format(s=subject, p=predicate, o=obj)
	elif option == 3:
		body = "SELECT ?{s} ?{p} WHERE {{ ?{s} ?{p} {o} }}".format(s=subject, p=predicate, o=obj)
	
	response = requests.post('http://localhost:8080/dbpedia/',
       data={'query': body})	
	
	# print the json in readable format
	# print(json.dumps(response.json(), indent=1))
	# print(response.text)
	return response.json()

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

def loader(): 
	"""
		Method for loading rule and load data into memory(cache)
	"""

	# load rule and generate a list of relations
	rules, relations = rule_selector("<dbo:author>", 1)
	predicate_map = {}
	
	for predicate in relations:
		# TODO: Make it asyn?
		sub, obj= "subject", "object"

		pred = trim(predicate)
		print(pred)

		if pred not in predicate_map:
			pyDatalog.create_terms(pred)
			predicate_map[pred] = 1

		response = pull_from_fuseki(sub, predicate, obj, 2)
		# cache(response, sub, pred, obj, predicate_map)

	knowledge(rules)

	return rules, relations

def trim(string):
	string = string.split(":")[1].strip().split(">")[0]
	string = string.replace("/", "")
	string = string.replace(".", "")
	return string.strip()

def knowledge(rules):
	# rules = [ "C(X,Z) <= A & B", "E(X,Z) <= C & D ", "F(X,Z) <= E & A", "C(X,Z) <= A(X,Y)"]

	rule_map = {}
	idb_set = set()
	

	# iterate thru all rules and find the idb and edb
	for index, rule in enumerate(rules):
	
		node = RuleNode(trim(rule))
		idb_set.add( node.left )

		rule_map[str(index)] = node

	# while rule_map is not empty
	while rule_map:
		to_remove = set()

		for key in list(rule_map.keys()):
			node = rule_map[key]

			if not idb_set.intersection(node.right_set):
				to_remove.add(node.left)
				del rule_map[key]
				
				# select node to do fancy things

		idb_set = idb_set.difference(to_remove)
		
		print(to_remove)
		print(idb_set)

def alogrithm(rules, relations):
	pass



if __name__ == "__main__":
	

	# sub, pred, obj= "subject", "predicate", "object"
	# response = pull_from_fuseki(sub, pred, obj, 0);
	# cache(sub, pred, obj)
	
	loader()
	pyDatalog.create_terms("X", "Y", "Z")
	# print(pyDatalog.ask("influenced" + '(X, Y)'))

	print(pyDatalog.ask('author' + '(X, "George_Orwell")'))

