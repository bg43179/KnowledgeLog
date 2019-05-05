"<db:Animal_Farm><dbo:author><db:George_Orwell>."

import re
import collections
import numpy

PRED_NAME = re.compile(r'<.*><(.*)><.*>\.')

SAMPLE_FACTOR = 0.02

predicates = collections.defaultdict(list)
with open("dbpedia.3.8.nt", 'r') as f:
    for line in f.readlines():
        result = PRED_NAME.match(line.rstrip())

        try:
            assert result
        except:
            print(line.rstrip())
            assert False

        pred = result.group(1)

        predicates[pred].append(line.rstrip())

sampled_predicates = collections.defaultdict(list)

for k, v in predicates.items():
    sample_size = int(SAMPLE_FACTOR * len(v))
    sample_size = sample_size if sample_size > 0 else 1
    for idx in numpy.random.choice(len(v), sample_size, replace=False):
        sampled_predicates[k].append(v[idx])

with open("dbpedia.3.8_0.02.nt", 'w') as f:
    for _, v in sampled_predicates.items():
        for l in v:
            f.write("%s\n" % l)
