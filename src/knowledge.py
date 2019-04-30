import copy
from tree import rule_selector
from node import RuleNode
from pyDatalog import pyDatalog
from request import pull_from_fuseki
import collections
import re
import functools
import loguru


def extract_tuple_from_fuseki_response(response):
    for instance in response['results']['bindings']:
        yield instance['subject']['value'].split(':')[0], instance['object']['value'].split(':')[0]


QUERY_PRED = re.compile(r'(.*)\(.*\)')


def eval_datalog(data, rule):
    """
    Evaluation using pyDatalog.
    :param data: a list of tuple string
    :param rule: a rule node
    :return: a list of resulting tuple string
    """
    assert isinstance(data, list)
    assert isinstance(rule, RuleNode)

    def extract_query_predicate(rule):
        return QUERY_PRED.match(rule).group(1)

    def db2str(tuples):
        return "\n".join(["+%s(%s,%s)" % (s, p, o) for (s, p, o) in tuples])

    def result2tuplestring(result):
        query_pred = extract_query_predicate(rule.rule)
        for (s, o) in result:
            yield (s, query_pred, o)

    pyDatalog.clear()
    pyDatalog.load(db2str(data) + '\n' + str(rule))
    # pyDatalog.create_terms()

    loguru.logger.debug(db2str(data) + '\n' + str(rule))
    loguru.logger.debug(rule.left+'(X, Y)')

    result = pyDatalog.ask(rule.left+'(X, Y)')

    return list(result2tuplestring(result))


def eval_prob_query(rules, input_db):
    """
    Evaluate datalog programs given rules and EDB
    :param rules:
    :param input_db:
    :return: A resulting output database
    """

    predicates = copy.deepcopy(input_db)

    def get_next_rule(rules):
        """
        Retrieve rule in order considering dependency
        :param rules: A list of rule node object
        :return:
        """
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
                if not idb_set.intersection(node.right_set):
                    yield node
                    head_counter[node.left] -= 1
                    if head_counter[node.left] == 0:
                        to_remove.add(node.left)
                    del rule_map[key]

            idb_set = idb_set.difference(to_remove)

    tuple2conf = {}

    def get_next_part_from_single_table(pred_name, num_splits=5):
        loguru.logger.debug('Trying to retrieve data for relation: %s' % pred_name)
        tuples = predicates[pred_name]
        sorted_tuples = sorted([(t, tuple2conf[t]) for t in tuples], key=lambda x: x[1])

        split_size = int(len(sorted_tuples) / num_splits)
        loguru.logger.debug('tuple_length: %d, num_splits: %d' % (len(sorted_tuples), num_splits))
        if split_size == 0:
            split_size = len(sorted_tuples)

        for x in range(0, len(sorted_tuples), split_size):
            yield list(map(lambda y: y[0], sorted_tuples[x:x + split_size])), \
                  float(
                      sum(map(lambda y: y[1], sorted_tuples[x:x + split_size])) / len(sorted_tuples[x:x + split_size]))

    def get_next_part_pair(pred1_name, pred2_name):
        for t1, avg1 in get_next_part_from_single_table(pred1_name):
            for t2, avg2 in get_next_part_from_single_table(pred2_name):
                yield t1 + t2, avg1 * avg2

    def store_intermediate_results(tuples, conf):
        """
        :param tuples: list of tuple string
        :param conf: confidence
        :return:
        """
        for (s, p, o) in tuples:
            predicates[p].add((s, p, o))
            tuple2conf[(s, p, o)] = conf

    def initialize_tuple2conf():
        for _, items in input_db.items():
            for t in items:
                tuple2conf[t] = 1

    initialize_tuple2conf()
    for rule in get_next_rule(rules):

        if len(rule.right_set) == 2:
            for data, conf in get_next_part_pair(list(rule.right_set)[0], list(rule.right_set)[1]):
                resulting_tuples = eval_datalog(data, rule)
                store_intermediate_results(resulting_tuples, conf * rule.conf)

        if len(rule.right_set) == 1:
            for t, avg in get_next_part_from_single_table(rule.right_set[0]):
                store_intermediate_results(t, avg * rule.conf)

        else:
            assert False

    return predicates, tuple2conf

PRED_NAME = re.compile('<dbo:(.*)>')

def main(query_relation="<dbo:author>", depth=2):
    loguru.logger.info('Start loading rules....')
    rules, relations = rule_selector(query_relation, depth)
    loguru.logger.info('Finish loading rules')

    def retrieve_data_from_relations(rlns):
        data = collections.defaultdict(set)
        for predicate in rlns:
            sub, obj = "subject", "object"
            resp = pull_from_fuseki(sub, predicate, obj, 2)

            cleaned_pred = PRED_NAME.match(predicate).group(1)
            for s, o in extract_tuple_from_fuseki_response(resp):
                data[cleaned_pred].add((s, cleaned_pred, o))
        return data

    def extract_confidence(db, conf):
        result = []
        for t in db[query_relation]:
            result.append((t, conf[t]))
        return result

    loguru.logger.info('Start loading predicates given rules....')
    predicates = retrieve_data_from_relations(relations)
    loguru.logger.info('Finish loading predicates given rules')

    loguru.logger.info('Start evaluating....')

    loguru.logger.info('Size of start database: %d' %
                       functools.reduce((lambda x, y: x + y), [len(v) for v in predicates.values()]))

    end_database, tuple_conf = eval_prob_query(rules, predicates)
    loguru.logger.info('Finish evaluating')

    loguru.logger.info('Size of end database: %d' %
                       functools.reduce((lambda x, y: x + y), [len(v) for v in end_database.values()]))

    tuple_with_conf = extract_confidence(end_database, tuple_conf)

    return sorted(tuple_with_conf, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    # a = PRED_NAME.match('<dbo:chairperson>')
    # print(a.group(1))
    main()
    # pyDatalog.load("+r('a','b')\na(X,Y)<=r(Y,X)")
    # print(pyDatalog.ask('e(X,Y)'))
