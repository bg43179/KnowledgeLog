import sys
import json
import requests

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
	return response.json()