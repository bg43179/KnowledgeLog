import sys
import json
import requests
from tree import rule_selector
from node import RuleNode, trim
from pyDatalog import pyDatalog
from request import pull_from_fuseki
import loguru
import collections


def cache(response, sub, predicate, obj, predicate_map={}):
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

    loguru.logger.debug(count)


def partition_cache(node, predicate_map, no_of_partition=5):
    """
        This method can load all the relation in one rule into memory.
        Divide all the relation into 5 different partition, each represent different probability
    """
    table = []

    for predicate in node.raw_set:

        predicates = []

        for num in range(no_of_partition):
            name = trim(predicate, 1, "r") + "__prob__" + str(num + 1)
            predicates.append(name)

            if name not in predicate_map:
                pyDatalog.create_terms(name)
                predicate_map[name] = 1

                if (num + 1) == no_of_partition:
                    # if data haven't been loaded into DB, add it from fuseki
                    sub, obj = "subject", "object"
                    predicate_map[predicates[-1]] = 1

                    # TODO: modify the string passed in
                    loguru.logger.debug(predicate)
                    response = pull_from_fuseki(sub, predicate, obj, 2)
                    cache(response, sub, predicates[-1], obj, predicate_map)

        table.append(predicates[:])


# Join two relations(or one relation)
# for i in range(len(table)):
# for j in range(len(table[0])):


# loguru.logger.debug(table)
# loguru.logger.debug(predicate_map)


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
        sub, obj = "subject", "object"

        pred = trim(predicate, 1, "r")
        loguru.logger.debug(pred)

        if pred not in predicate_map:
            pyDatalog.create_terms(pred)
            predicate_map[pred] = 1

        response = pull_from_fuseki(sub, predicate, obj, 2)
        cache(response, sub, pred, obj, predicate_map)


def eval(data, rule):
    pass


tuple2conf = {}
predicates = {}


def get_next_pair(pred1_name, pred2_name):

    def get_next_part_from_single_table(pred_name, num_splits=5):

        tuples = predicates[pred_name]
        sorted_tuples = sorted([(t, tuple2conf[t]) for t in tuples], key=lambda x: x[1])

        split_size = int(len(sorted_tuples)/num_splits)
        for x in range(0, len(sorted_tuples), split_size):
            yield list(map(lambda y: y[0], sorted_tuples[x:x + split_size])), \
                  float(sum(map(lambda y: y[1], sorted_tuples[x:x + split_size]))/len(sorted_tuples[x:x + split_size]))

    for t1, avg1 in get_next_part_from_single_table(pred1_name):
        for t2, avg2 in get_next_part_from_single_table(pred2_name):
            pass


    pass


def knowledge(rules):

    def get_next_rule(rules):
        rule_map = {}
        idb_set = set()
        head_counter = collections.defaultdict(lambda: 0)

        for index, rule in enumerate(rules):
            node = RuleNode(rule[0], rule[1])
            idb_set.add(node.left)
            head_counter[node.left] += 1
            rule_map[str(index)] = node

        while rule_map:
            to_remove = set()
            for key in list(rule_map.keys()):
                node = rule_map[key]
                # loguru.logger.debug(node.right_set)
                if not idb_set.intersection(node.right_set):
                    yield node
                    head_counter[node.left] -= 1
                    if head_counter[node.left] == 0:
                        to_remove.add(node.left)
                    del rule_map[key]

            idb_set = idb_set.difference(to_remove)

    for rule in get_next_rule(rules):
        loguru.logger.info(rule)


if __name__ == "__main__":
    # sub, pred, obj= "subject", "predicate", "object"
    # response = pull_from_fuseki(sub, pred, obj, 0);
    # cache(sub, pred, obj)

    # loader()
    # partition_loader()
    pyDatalog.create_terms("X,Y")
    # loguru.logger.debug(pyDatalog.ask("influenced" + '(X, Y)'))

    # loguru.logger.debug(pyDatalog.ask('author' + '(X, "George_Orwell")'))
    pyDatalog.load(
        "+r('a','b')\na(N,M)<=r(M,N)"
    )
    # print(pyDatalog.ask("a(X,Y)"))

    pyDatalog.clear()

    print(pyDatalog.ask("a(X,Y)"))
