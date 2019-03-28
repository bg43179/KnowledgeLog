### Todo
* [ ] Transform tsv data to tdb and allowed it to be loaded by fuseki.
* [ ] Desgin data structure/algorithm to load rule (Say we want to query launchSite, and country + countryOrigin => launchSite. Have to also query country and countryOrigin. Find proper stopping criteria.)

Idea: 
1. Select predicate to be queried
2. Load rule
3. Load data


-------------------------------------------------------------------------

03/14/2019
* [V] Store data retrieving from DBpedia
* [V] Set up Jena server for reading data from RDF
* [V] Set up Jena server for supporting RESFUl API
* [ ] Use SPARQL to query RDF

-------------------------------------------------------------------------

03/07/2019
* [ ] Read [Datalog +- paper](https://openproceedings.org/2009/conf/icdt/CaliGL09.pdf?fbclid=IwAR1WQzGlSBHKUQdRs034KYFNUEI7_XRPM_vxG9SwkJ8OV5TwQCdUpKuAuRk) and see the 4 new features it suggested.
* [ ] Use PyDatalog to read Knowledge Base files.
* [ ] See if LogicBlox has the 4 features in Datalog +- paper.
