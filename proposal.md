KnowledgeLog: An efficient datalog inference engine for knowledge base reasoning

Paul Luh luh@wisc.edu
Han Wang hwang729@wsic.edu
Yahn-Chung Chen chen666@wisc.edu


### Short description of the problem

To efficiently apply datalog to query knowledge base, users are required to have in-depth understandings in datalog and it subsequently becomes a barrier for the ubiquity of datalog. In this project, a user-friendly framework, KnowledgeLog, is proposed to serve as a interface for users without datalog knowledge to easily query knowledge base. Users will be able to query direct and indirect relations with predefined modules.

### Method

From an existing knowledge base dataset, we are trying to use datalog concepts to do fact assertion. For example, if we have the facts <Barack Obama, studied in, Columbia University> and <Columbia University, located in, New York City> in the dataset, we can know that <Barack Obama, lived in, New York City> is another fact though it’s not in the dataset. We will develop a new python package on top of pyDatalog[2]. Currently, a user should declare the join relationship before querying using pyDatalog. However, we want to return the fact without user declaration but do the join transparently. 

### Evaluation

Given a fixed set of fact-assertion queries, we will compare our system with several existing frameworks such as LogicBlox[3] and pyDatalog in terms of functionality, performance, and accuracy. In particular, we will be especially interested in testing facts that are not explicitly mentioned but can only be inferred through tuples occurred in several different relations.  Furthermore, since we also aim to build a system that is user-friendly, we plan to organize user studies where we invite users from different backgrounds to performs knowledge reasoning task through our user interface.  

###  Reference

[1] knowledge Vault: A Web-Scale Approach to Probabilistic Knowledge Fusion https://www.cs.ubc.ca/~murphyk/papers/kv-kdd14.pdf
[2] pyDatalog https://sites.google.com/site/pydatalog/
[3] LogicBlox https://developer.logicblox.com/
