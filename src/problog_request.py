from rule import getRules
import re
import requests
import sqlite3
import os
from problog.program import PrologString
from problog import get_evaluatable

def problog_model(rules):
    model = ":- use_module(library(db)).\n:- sqlite_load('tmp.db').\n"
    for rule in rules:
        model += "{}::{}\n".format(rule[1], rule[0])
    return model

def run_problog(rules, target_rule, target_subject):
    model_string = problog_model(rules)
    model_string += "query({}(\'{}\',_)).".format(target_rule, target_subject)
    print(model_string)
    result = get_evaluatable().create_from(PrologString(model_string)).evaluate()
    return result

def pull_from_fuseki(subject, predicate, obj):
    body = "SELECT ?{s} ?{o} WHERE {{ ?{s} {p} ?{o} }}".format(s=subject, p=predicate, o=obj)
    response = requests.post('http://localhost:8080/dbpedia/', data={'query': body})
    return response.json()

def save_to_sqlite(response, predicate, db_con):
    print(predicate)
    cur = db_con.cursor()
    cur.execute('CREATE TABLE {} (subject TEXT NOT NULL, object TEXT NOT NULL);'.format(predicate))
    rows = response['results']['bindings']
    for row in rows:
        subject = row['subject']['value'][3:]
        obj = row['object']['value'][3:]
        insert_query = "INSERT INTO {} (subject, object) VALUES (\"{}\", \"{}\");".format(predicate, subject, obj)
        cur.execute(insert_query)
    db_con.commit()

def loader(con, relations):
    for predicate in relations:
        sub, obj= "subject", "object"

        response = pull_from_fuseki(sub, predicate, obj)
        save_to_sqlite(response, predicate[5:-1], con)

if __name__ == "__main__":
    con = sqlite3.connect('tmp.db')
    #RULE = '<dbo:keyPerson>'
    RULE = '<dbo:notableWork>'
    #SUBJECT = '<db:National_Inclusion_Project>'
    SUBJECT = '<db:Ernest_Hemingway>'

    try:
        rules, relations = getRules(RULE, rule_type="ProbLog", threshold=0.5)
        if len(rules) > 0:
            loader(con, relations)
            result = run_problog(rules, RULE[5:-1], SUBJECT[4:-1])
            sorted_result = sorted(result.items(), key=lambda kv: kv[1], reverse=True)
            print()
            print('Result:')
            for res in sorted_result:
                print(res)
        else:
            loader(con, [RULE])
        cur = con.cursor()
        cur.execute('SELECT object FROM {} WHERE subject = \'{}\''.format(RULE[5:-1], SUBJECT[4:-1]))
        rows = cur.fetchall()
        print("Found in database:\n", rows)
        print()
        con.close()
        os.remove('tmp.db')
    except Exception as e:
        print(e)
        os.remove('tmp.db')
