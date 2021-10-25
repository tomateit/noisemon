# Project that listens and makes some notes
The project is very very WIP; I do research in `notebooks/`, you can check out:
- `building_faiss_index` - how to do entity linking with faiss and transformer


#### This is version 1 of the app; the main nuances, which will not be the case in further versions, are the following:
+ The app intends to retrieve data by itself (will be connected to common data infrastructure later)
+ ...so the only data source now is telegram channels.
+ App uses local sqlite database as a form of a cache

### What I wanna do:
1. Read the data stream from telegram channels
- Subscribe to a list of channels,
- Listen to updates 
    1. Get new text
    2. Check requirements (e.g. not to be a repost or contain blacklisted stuff)
    3. Parse and analyze
2. Matching to organizations
- The entitites are retrieved from wikidata
    - entity matching
    - Check if there is a ticker
3. Store known orgs and relevant stats
- Put into db chunks in form of "organization: date of mention"
- Demonstrate aggregated stats on a webpage

### How the app currently works
It has 2 phases of functioning:
1. The faiss index is created based on pre-labeled dataset and th app is functioning with static vector set.
2. In addition, online learning feature adds extra vectors and entities based on a strategy, thus extending range and precision of percepted entities.

### Currently working on:
+ Creating pre-labeled dataset
+ Dumping faiss index (todo: check consistency in db and index)

### Next on the list:
+ API
+ UI

### Pending improvements
+ Longer sequences processing: currently we are truncating incoming texts up to model's limit
+ Incoming texts filtration

-----------
### To run tests
`python -m unittest discover ./noisemon -p '*tests.py'`
