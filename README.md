# NOISEMON (1.0)
## Reactive Entity Linking Pipeline
The core of this app is adaptive mechanism of Vector Index-based entity linking.

### Subtasks
1. Identify entities - NER
2. Link the entities - NEL

### Operates based on a database-stored dataset
The data model of the dataset:
- `Resource` - resource type and meta, say, lineage
- `ResourceLink` - Resources, like newspapers or blogs, usually have their texts identified somehow; this works for datasets too - say, meta-row
- `Document` - Well, the text entry per se
- `Entity` - Wikidata Entity representation, as a common denominator
- `Mention` - the link between entity and document; locates entity within the text

For the linker to operate, you provide it with a database access (project's DataRepository compatible), with data uploaded there (scripts are available too)


### What the app currently does:
1. It listens to the stream of text messages
2. Performs text processing for NER:
    - The custom transformer+ner pipeline is used to extract named entities
3. Named entities lined with Wikidata entities via NEL mechanism:
    - The app creates and holds vector index, which helps to match entities by vector similarity and text likeliness with other entities' vectors, thus achieving both character-based and semantic comparasion.
    - I could basically match by substring matching, but vector-enabled matching allows to disambiguate entities which have similar names.
4. As a side effect it creates a NER+NEL dataset:
    - Each match is recoreded and allows to make a connection between wikidata entity and mentioned entity
5. One of population strategies is applied for online learning of new entities
    - This makes our set of known entities to grow with time.


### Technical nuances
1. The vectos are saved in database, so they are persistent between restarts.
2. Initial vector population from pre-labeled dataset is necessary, you can create a dataset using some heuristics.
3. In addition, online learning feature adds extra vectors and entities based on a strategy, thus extending range and precision of percepted entities, yet it leads to vector and database growth.
4. The storage is designed in a way you can retrieve enough data to create a pre-labeled NER+NEL dataset from the data you have, which may be helpful for iterative improvement of NER model.


### WIP:
+ Integration with KB:
    - Based on https://arxiv.org/abs/2110.06176 , entity vectors contain some sort of factual information, linked with the particular mention of an entity. This somewhat enables us to do the following two things:
        1. Make a transition from Mention Vector to KB triplet to populate KB
        2. Make a transition from KB triplet to -> Mention Vector to -> original text
    - These transitions would allow us to create programmatic means to increase consistency between the world of unstructural flows of natural language texts and the world of structural knowledge. This, per se, does not enable us to perform a fact checking, as data in KB may be outdated, and information in texts may be just wrong, but such system would provide us a bunch of useful tools, e.g. notification on inconsisteny between KB and text.

### Pending improvements
+ Fix incostistent logging means.
+ Fix test running and test framework unification.
+ Vector ageing capabilities (not all learned vectors are actually useful for search).

-----------
### To run tests
`python -m unittest discover ./noisemon -p '*.tests.py'`
