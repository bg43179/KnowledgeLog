import pandas as pd
from collections import Counter
# rule info source
df = pd.read_csv("rules_info.csv")

# parameter
THRE = 0.7
MAX_SUBJECTS = 2

def getRules(target):
    # C(X,Y) <= A(X, Y) & B (Y,Z)

    def next_level_rules(target, conf, levels, rules):
        # no self-cycle more than MAX_SUBJECTS times
        if levels[target] >= MAX_SUBJECTS: return [([target], rules, conf)]
        new_levels = levels + Counter({target:1})

        # get target rules
        target_rules = df.loc[df['object'] == target]

        # get possible rules
        result =[([target], rules, conf)]
        for tidx in target_rules.index:
            cur_conf = conf*target_rules.loc[tidx]['conf_pca']
            if cur_conf >= THRE:
                rule = target_rules.loc[tidx]
                subject1, subject2 = rule['subject1'], rule['subject2']
                cur_rules = rules+[tidx]
                s1_list = next_level_rules(subject1, cur_conf, new_levels, cur_rules)
                s2_list = next_level_rules(subject2, cur_conf, new_levels, cur_rules) if type(subject2) == str else []
                if not len(s2_list):
                    result.extend(s1_list)
                else:
                    for s1 in s1_list:
                        for s2 in s2_list:
                            i, prob = 0, 1
                            for i, (r1, r2) in enumerate(zip(s1[1], s2[1])):
                                if r1 != r2: break
                                prob *= df.loc[r1]['conf_pca']
                            for r2 in s2[1][i:]:
                                prob *= df.loc[r2]['conf_pca']

                            if prob >= THRE:
                                result.append((s1[0]+s2[0], s1[1]+s2[1][i:], prob))

        return result

    # get all rules with the object target
    res = next_level_rules(target, 1, Counter(), [])

    # generate the formatted output
    # rules : List[tuple] ([(rule, conf_pca)])
    # explored : set
    explored = set([target])
    selected_id = set()
    for rc in res:
        explored.update(rc[0])
        selected_id.update(rc[1])
    rules_df = df.loc[selected_id, ['rule', 'conf_pca']]

    return [tuple(x) for x in rules_df.values], explored
