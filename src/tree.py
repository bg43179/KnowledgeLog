import csv
from collections import deque
from node import RuleNode
import config

class TreeNode():
	def __init__(self, value):
		self.value = value
		self.children = {}
		self.rules = {}

	def add_child(self, child, rule, confidence):
		self.children[child.value] = child
		self.rules[rule] = (rule, confidence)

	def get_children(self):
		return self.children.values()
	
	def get_rule(self):
		return self.rules.values()


def get_node(value, tree_map):
	"""
		Create new node or reuse the node in the tree_map
	Args:
	    value: name of the relation
	    tree_map: a dictionary with relation-node mapping
	Returns:
	    node: either the newly created node or the node existing in tree_map
	"""	

	if value not in tree_map:
		node = TreeNode(value)
		tree_map[value] = node
	else:
		node = tree_map[value]
	return node

def build_tree(filename = '../rules.csv'):
	"""
		Build a tree for level-order traversal

	Args:
	    filename: the file want to be parser

	Returns:
	    tree_map: a dictionary with relation-node mapping
	"""	

	tree_map = {}

	# open file
	with open(filename, 'r') as fp: 
		next(fp)
		reader = csv.reader(fp)
		
		for row in reader:			
			
			[first, second, outcome, rule, confidence] = extractor(row)		

			# if any node is created, reuse it. 
			if confidence > config.score_threshold:
				parent = get_node(outcome, tree_map)
			
				first_child = get_node(first, tree_map)
				parent.add_child(first_child, rule, confidence)

				# second may not be null
				if second != None:
					second_child = get_node(second, tree_map)
					parent.add_child(second_child, rule, confidence)

	return tree_map

def extractor(row):
	"""
		Transform the input csv to desired format

	Args:
	    row: input csv, [i.e. "influenced(X,Y) <= author(X,Y) & influencedBy(Y,Z)", 0.4]
	
	Returns:
	    first: first relation
	    second: second relation(may not exits)
	    outcome: outcome relation
	    rule: the raw rule without modification
	    confidence: confidence score of a single rule
	"""
	rule = row[0].strip()
	rule_list = rule.split("<=")
	confidence = float(row[1].strip())
			
	outcome = rule_list[0].split("(")[0].strip()
	
	reason = rule_list[1].split("&")
	first = reason[0].split("(")[0].strip()
	second = None if len(reason) == 1 else reason[1].split("(")[0].strip()

	return [first, second, outcome, rule, confidence]

def rule_selector(target, step=2):
	"""
		Transform the input csv to desired format
	
	Args:
	    target: the predicate users want to find
	    step: depth of the tree that users want to traverse

	Returns:
		rules: a list with all the related rules
		relations: all the relations in rules
	"""

	# Construct Tree 
	tree_map = build_tree()

	level = 0
	rules = []

	explored = set([target])
	queue = deque([tree_map[target]])
	
	# Level-order traversal
	while queue and level < step:
		size = len(queue)
		
		for i in range(size):
			curr = queue.popleft()
			
			rules.extend(remove_cycle(curr.get_rule(), explored))
			# rules = list(filter(lambda x: x[1] > 0.4, rules))
			
			if not rules:
				return [], explored
			# Add non visited child 
			for child in curr.get_children():

				if child.value in explored:
					continue
				queue.append(child)
				explored.add(child.value)

		level += 1

	# rules = list(filter(lambda x: x[1] > 0.4, rules))
	return rules, explored

def remove_cycle(rules, explored):
	rules = list(map(lambda x: RuleNode(x[0], x[1]), rules))
	res = []

	for node in rules:
		# if empty, not explored yet!
		if node.raw_set.intersection(explored):
			continue
		
		res.append((node.rule, node.conf))

	return res

if __name__ == "__main__":
	
	# rule = "influenced(X,Y) <= author(X,Y) & influencedBy(Y,Z)"

	# root = TreeNode("influenced")
	# root.add_child("author", "influenced(X,Y) <= author(X,Y) & influencedBy(Y,Z)")
	# root.add_child("influencedBy", "influenced(X,Y) <= author(X,Y) & influencedBy(Y,Z)")
	
	# tree_map = build_tree()
	# print(tree_map.keys())
	# print(root.get_rule())
	# print(", ".join(rule for rule, conf in tree_map["author"].get_rule()))
	# print(", ".join(i.value for i in tree_map["author"].get_children()))
		

	# print(rule_selector("influenced", 1)[0])
	for i in rule_selector("<dbo:notableWork>", 2)[0]:
		print(i)
	# print(rule_selector("<dbo:author>", 2)[0])
