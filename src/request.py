import sys
import json
import requests
from pyDatalog import pyDatalog


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
		body = "SELECT ?{s} ?{p} ?{o} WHERE {{ ?{s} ?{p} ?{o} }} LIMIT 25".format(s=subject, p=predicate, o=obj)
	elif option == 1:
		body = "SELECT ?{p} ?{o} WHERE {{ {s} ?{p} ?{o} }} LIMIT 25".format(s=subject, p=predicate, o=obj)
	elif option == 2:
		body = "SELECT ?{s} ?{o} WHERE {{ ?{s} {p} ?{o} }} LIMIT 25".format(s=subject, p=predicate, o=obj)
	elif option == 3:
		body = "SELECT ?{s} ?{p} WHERE {{ ?{s} ?{p} {o} }} LIMIT 25".format(s=subject, p=predicate, o=obj)
	
	# print(body)
	
	response = requests.post('http://localhost:8080/dbpedia/',
       data={'query': body})
	
	# print(response.text)
	# print the json in readable format
	print(json.dumps(response.json(), indent=1))
	return response.json()

def cache(response, sub, predicate, obj, predicate_map = {}):
	"""
		Method for pulling data form fuseki, support 4 different requests body

	Args:
	    subject: subject
	    predicate: predicate
	    obj: object 
	    predicate: Use for tracking if the relation(predicate) talbe already exist

	Returns:
	    return a json 

	"""
	# first create term for all the predicate
	
	# add a instance in this format (+prdicate(subject, object))
	for index, instance in enumerate(response['results']['bindings']):	
		
		current_pred = predicate
		item = {}
		
		for key, value in instance.items():
			# creat a new relation table if the predicate is not exist
			if key == predicate:
				if key not in predicate_map:
					pyDatalog.create_terms(value["value"].split(":")[1])
					predicate_map[value["value"].split(":")[1]]= 1
				current_pred = value["value"].split(":")[1]

			if key == sub:
				item[sub] = value["value"].split(":")[1]
				
			if key == obj:
				item[obj] = value["value"].split(":")[1]
		
		# add the fact
		pyDatalog.assert_fact(current_pred, item[sub], item[obj])
	
	# print(current_pred)
	# print(pyDatalog.ask(current_pred + '("George_Orwell", X)'))
	print(predicate_map)
	# pass

def loader(): 
	"""
		Method for loading rule and load data into memory(cache)
	"""

	pyDatalog.load("influenced(X,Y) <= author(X,Y) & influencedBy(Y,Z)")
	rules = ["influenced" ,"author", "influencedBy"]
	
	predicate_map = {}
	
	for predicate in rules:
		# Have to make it asyn
		sub, obj= "subject", "object"

		if predicate not in predicate_map:
			pyDatalog.create_terms(predicate)
			predicate_map[predicate]= 1

		response = pull_from_fuseki(sub, "<dbo:" + predicate +">", obj, 2)
		cache(response, sub, predicate, obj, predicate_map)
		

if __name__ == "__main__":
	

	# D(x,y) <= R(X,Y) S(Y,Z);


	# sub, pred, obj= "subject", "predicate", "object"

	# sub = "subject"
	# pred = "<dbo:author>"
	# obj = "<db:George_Orwell>"
	
	# rule_loader: load rule, generate a list of rule for pull from fueski
	# rule_loader()
	# response = pull_from_fuseki(sub, pred, obj, 0);
	# cache(sub, pred, obj)
	loader()

	pyDatalog.create_terms("X", "Y", "Z")
	# print(pyDatalog.ask("influenced" + '(X, Y)'))

	
	# rule_loader()
	# print(pyDatalog.ask("influenced" + '(X, Y)'))
	print(pyDatalog.ask("influenced" + '("George_Orwell", X)'))

