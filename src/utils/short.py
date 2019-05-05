
op = open("../rules_2000.csv", "w")
count = 0

with open("../rules.csv", 'r') as f:
	for line in f.readlines():
		if count % 2 == 0:
			op.write(line)
		count += 1	


op.close()
