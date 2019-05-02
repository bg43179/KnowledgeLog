import pandas as pd
from collections import Counter
import warnings
warnings.simplefilter("ignore")

RULE_FILE = "rules_info.csv"
REDUCE_CYCLE = True

def getRules(target, threshold = 0.5, max_subjects = 1, rule_type = 'pyDatalog'):
    # C(X,Y) <= A(X, Y) & B (Y,Z)
    # rule_type = pyDatalog, ProbLog

    # rule info source
    df = pd.read_csv(RULE_FILE)
    df = df[df['conf_pca'] >= threshold]

    def next_level_rules(tar, conf, levels, rules):
        # no self-cycle more than MAX_SUBJECTS times
        if levels[tar] >= max_subjects: return [([tar], rules, conf)]
        new_levels = levels + Counter({tar:1})

        # get target rules
        target_rules = df[df['object'] == tar]

        # get possible rules
        result =[([tar], rules, conf)]
        for tidx in target_rules.index:
            rule = target_rules.loc[tidx]
            cur_conf = conf*rule['conf_pca']
            if cur_conf >= threshold:
                subject1, subject2 = rule['subject1'], rule['subject2']
                cur_rules = rules + [tidx]
                s1_list = next_level_rules(subject1, cur_conf, new_levels, cur_rules) \
                            if (subject1 != target and REDUCE_CYCLE) or not REDUCE_CYCLE else []
                s2_list = next_level_rules(subject2, cur_conf, new_levels, cur_rules) \
                            if type(subject2) == str and ((subject2 != target and REDUCE_CYCLE) or not REDUCE_CYCLE) else []
                if not len(s2_list):
                    result.extend(s1_list)
                    continue
                for s1 in s1_list:
                    for s2 in s2_list:
                        i, prob = 0, 1
                        for i, (r1, r2) in enumerate(zip(s1[1], s2[1])):
                            if r1 != r2: break
                            prob *= df.loc[r1]['conf_pca']
                        for r2 in s2[1][i:]:
                            prob *= df.loc[r2]['conf_pca']

                        if prob >= threshold:
                            result.append((s1[0]+s2[0], s1[1]+s2[1][i:], prob))

        return result

    # get all rules with the object target
    res = next_level_rules(target, 1, Counter(), [])

    if len(res) == 1:
        print("No related rules found.")
        return list(), set()

    # generate the formatted output
    # rules : List[tuple] ([(rule, conf_pca)])
    # explored : set
    explored = set([target])
    selected_id = set()
    for rc in res:
        explored.update(rc[0])
        selected_id.update(rc[1])

    if rule_type == 'pyDatalog':
        rules_df = df.loc[selected_id, ['rule', 'conf_pca']]
        return [tuple(x) for x in rules_df.values], explored

    elif rule_type == 'ProbLog':
        rules_df = df.loc[selected_id]
        dbo_transform = lambda x: x[5:-1] if type(x)==str else None
        rules_df['prob_rule_str'] = df['object'].apply(dbo_transform) + '(A,B) :- ' \
                + df['subject1'].apply(dbo_transform) + '(' + df['subject1_a'].str.upper() + ',' + df['subject1_b'].str.upper() + ')'

        rules_df['prob_rule_str'].loc[rules_df['subject2'].notnull()] \
                = rules_df['prob_rule_str'] + ', ' + rules_df['subject2'].apply(dbo_transform) \
                + '(' + rules_df['subject2_a'].str.upper() + ',' + rules_df['subject2_b'].str.upper() + ')'
        rules_df['prob_rule_str'] = rules_df['prob_rule_str'] + '.'
        rules_df = rules_df[['prob_rule_str', 'conf_pca']]
        return [tuple(x) for x in rules_df.values], explored
    else:
        raise NameError('rule_type should be \'pyDatalog\' or \'ProbLog\'.')

if __name__ == "__main__":
    print(getRules("<dbo:author>"))
