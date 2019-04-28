class RuleNode():
	def __init__(self, rule, conf=None):
		
		self.rule = rule
		rule = rule.split("<=")
		
		right = rule[1].split("&")

		self.right_set =  set([trim(right[0], 1, "r")]) if len(right) == 1 else set([trim(right[0], 1, "r"), trim(right[1], 1, "r")])
		self.raw_set = set([trim(right[0], 2,), trim(right[1], 2,)]) if len(right) == 2 else set([trim(right[0], 2)])
		# self.raw_right_set = set([trim(right[0], 2,), trim(right[1], 2,)]) if len(right) == 2 else set([trim(right[0], 2)])
		# self.raw_all_set = set([rule[0], right[0], right[1]]) if len(right) == 2 else set([rule[0], right[0]])
		
		self.right = rule[1].strip()
		self.left = trim(rule[0], 1, "r")
		self.conf = conf

def trim(string, option=1, replace="f"):
	
	"""
		string: predicate i.e."<dbo:launchSite>(a, b)
	"""

	# get rid of everything => launchSite
	if option == 1: 
		string = string.split(":")[1].strip().split(">")[0]
	# get rid of parentheses => <dbo:launchSite>
	elif option == 2:
		string = string.split("(")[0]


	if replace == "r":
		string = string.replace("/", "")
		string = string.replace(".", "")


	return string.strip()