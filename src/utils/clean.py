op = open('dbpedia.3.8.nt', "w")

with open('dbpedia.3.8.tsv') as fp:
	for line in fp:
		line = line.replace("	", "")
		line = line.replace("\n", ".")
		op.write(line + "\n")
		print(".", end=' ')

op.close()
