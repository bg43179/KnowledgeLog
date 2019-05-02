import re

class RuleNode():
    def __init__(self, rule, conf=None):
        # Give rule: "<dbo:influenced(X,Y)> <= <dbo:influencedBy(X,Y)> & <dbo:author(X,Y)>"
        self.rule = rule
        
        rule = rule.split("<=")
        right = rule[1].split("&")

        # right_set:{"influencedBy", "author"}
        self.right_set = set([trim(right[0], 1, "r")]) if len(right) == 1 else set(
            [trim(right[0], 1, "r"), trim(right[1], 1, "r")])
        
        # raw_set:{"<dbo:influencedBy>", "<dbo:author>""}
        self.raw_set = set([trim(right[0], 2,), trim(right[1], 2,)]) if len(right) == 2 else set([trim(right[0], 2)])
        
        # right: "<dbo:influencedBy(X,Y)> & <dbo:author(X,Y)>"
        self.right = rule[1].strip()

        # left: "influenced"
        self.left = trim(rule[0], 1, "r")
        self.raw_left = trim(rule[0], 2,)
        self.conf = conf


    def __repr__(self):
        return repr((self.rule, self.conf))

    def __str__(self):
        output = ""
        flag = False
        for i in range(len(self.rule)):
            if self.rule[i] == '(':
                flag = True
            if flag:
                output += self.rule[i].upper()
            else:
                output += self.rule[i]
            if self.rule[i] == ')':
                flag = False


        output = output.replace('.', '')
        output = output.replace('/', '')
        output = output.replace('<dbo:', '')
        output = output.replace('<http:', '')
        output = output.replace('>', '')

        return output


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
