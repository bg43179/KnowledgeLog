import sys
import json
import requests
from pyDatalog import pyDatalog


# Pull data from Fueski
def pull_from_fuseki(subject, predicate, obj):
	# body = "SELECT ?{s} ?{p} ?{o} WHERE {{ ?{s} ?{p} ?{o} }} LIMIT 25".format(s=subject, p=predicate, o=obj)
	body = "SELECT ?{s} {p} {o} WHERE {{ ?{s} {p} {o} }} LIMIT 25".format(s=subject, p=predicate, o=obj)
	# print(body)
	
	response = requests.post('http://localhost:8080/dbpedia/',
       data={'query': body})
	
	# print the json in readable format
	# print(json.dumps(response.json(), indent=1))
	return response.json()

def cache(subject, predicate, obj):
	# first create term for all the preidcate
	predicate_map = {}
	# add a instance in this format (+prdicate(subject, object))
	for index, instance in enumerate(response['results']['bindings']):	
		
		current_pred = ""
		item = {}
		
		for key, value in instance.items():
			# creat a new relation table if the preidcate is not exist
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

def rule_loader(): 
	pyDatalog.load("influenced(X,Y) <= author(X,Y) & influencedBy(Y,Z)")
	pass

def gen_datalog():
	pass

def user_input():
	pass


if __name__ == "__main__":
	

	# D(x,y) <= R(X,Y) S(Y,Z);


	# sub = "subject"
	# pred = "predicate"
	# obj = "object"

	sub = "subject"
	pred = "<dbo:author>"
	obj = "<db:George_Orwell>"
	# Different 

	response = pull_from_fuseki(sub, pred, obj);
	cache(sub, pred, obj)

	pyDatalog.create_terms("X", "Y", "Z")
	# print(pyDatalog.ask("influenced" + '(X, Y)'))

	
	# rule_loader()
	# print(pyDatalog.ask("influenced" + '(X, Y)'))
	# print(pyDatalog.ask("influenced" + '("George_Orwell", X)'))

