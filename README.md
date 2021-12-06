# NOISEMON (0.4)
## Project that reads and makes some notes
The core of this app is adaptive mechanism of Vector Index-based entity linking with online population.


#### This is a service, which means:
+ It has quite limited purpose now: find entities in provided texts and link them to some wikidata entities.
+ Components are quite independent and (as I tried most) not coupled, 
+ ... so one basically can use it as a standalone script
+ ... yet it is designed to work with some database
+ The app is intended to be build into some data exchange framework (in this case - RabbitMQ), it has no data retrieving capabilities


### What the app does:
1. Listens to the stream of text messages
2. Performs spaCy-based text processing:
    - The custom transformer+ner pipeline is used to extract named entities
    - Entities are matched by vector similarity and text likeliness with other entities' vectors
    - Each match is recoreded and allows to make a connection between wikidata entity and mentioned entity
    - I could basically match by substring matching, but vector-enabled matching allows to disambiguate entities which have similar names.
3. One of population strategies is applied for online learning of new entities


### Nuances
1. The vectos are saved in database, so they are persistent between restarts, even though the vector index is in-memory.
2. Initial vector population from pre-labeled dataset is helpful, though you can technically start for scratch with an empy database.
3. In addition, online learning feature adds extra vectors and entities based on a strategy, thus extending range and precision of percepted entities.
4. The storage is designed in a way you can retrieve enough data to create a pre-labeled NER+NEL dataset from the data you have.


### Pending improvements
+ Fix incostistent logging means.
+ Fix test running and test framework unification.
+ Vector ageing capabilities (not all learned vectors are actually useful for search).

-----------
### To run tests
`python -m unittest discover ./noisemon -p '*.tests.py'`
