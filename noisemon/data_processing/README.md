# Data Processing Unit

## The data processing flow
0. Precomputed embeddings for entities
1. The news article/post probably has some formal signs of entity discussed in, e.g. ticker.
    + Those shall be extracted, checked and kept for further steps
2. Company names are to be extracted by NER tools:
    + We match them with KG entities, and then compare entity tickers with extracted ones. This may aid with omonimy resolution.
3. Thos marked as ORG by NER tools, if unmatched, are subject for further processing:
    + We either can retrieve more embeddings into our embeddings cache
    + or skip/blacklist it
4. Same for tickers

## Summary of units
1. List of entities, that are in KG
    + Lookup may be performed as by name, or by ticker
2. Stored embeddings for them with fast lookups
3. Results storage
