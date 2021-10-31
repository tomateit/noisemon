# Noisemon (0.3)
## Project that listens and makes some notes
The core of this app is adaptive mechanism of faiss-based entity linking with online population and flexible ageing capabilities.


#### This is version 1 of the app; the main nuances, which will not be the case in further versions, are the following:
+ The app intends to retrieve data by itself (not what I usually prefer, but this way it works as standalone 'monolith')
+ ...so the only data source now is telegram channels.
+ App uses local sqlite database

### What the app does:
0. Initializes a telegram accounts
    - Subscribe to a list of channels, specified in `telegram_channels.txt` as line-separated list of links
    - Unsubscribe of those unspecified in the list
1. Read the data stream from telegram channels
2. Match entities
    - The core currently is spacy NER model for russian
    - Entities are matched by vector similarity and text likeliness
    - Each match is recoreded
3. One of population strategies is applied for online learning of new entities


### Nuances
1. The vector + index are pre-saved in database, though you can technically start for scratch
2. In addition, online learning feature adds extra vectors and entities based on a strategy, thus extending range and precision of percepted entities.
3. The database is so you can from time to time pause, purge unused or rarely used vectors and relaunch quite easy. This will prevent vector index to grow unlimitedly.

### Currently working on:
+ Creating pre-labeled dataset


### Next on the list:
+ API
+ UI

### Pending improvements
+ Longer sequences processing: currently we are truncating incoming texts up to model's limit
+ Incoming texts filtration
+ Fix incostistent logging means

-----------
### To run tests
`python -m unittest discover ./noisemon -p '*tests.py'`
