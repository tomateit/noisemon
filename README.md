# Project that listens to and makes some notes

## This is version 1 of the app; the main nuances, which will not be the case in further versions, are the following:
+ The app intends to retrieve data by itself
+ App uses local sqlite database as a form of a cache

### What we do:
1. Read the data stream from telegram channels
- Subscribe to a list of channels,
- Listen to updates 
    1. Get new text
    2. Check requirements (e.g. not to be a repost or contain blacklisted stuff)
    3. Parse and analyze
2. Matching to organizations
- The entitites are retrieved from dbpedia
    - entity matching
    - Check if there is a ticker
3. Store known orgs and relevant stats
- Put into db chinks in form of "organization: date of mention"
- Demonstrate aggregated stats on a webpage

### Currently working on:
+ Data retrieval and processing
### Next on the list:
+ API
+ UI