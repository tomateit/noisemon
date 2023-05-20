from typing import List, Optional
from pydantic import BaseModel


class Entity(BaseModel):
    boundaries: List[int]  # tuple containing the of the surface form of the entity
    surfaceform: str
    uri: str
    annotator: str  # the annotator name used to detect this entity [NER,DBpediaspotlight,coref]



class Triple(BaseModel):
    sentence_id: int  # integer shows which sentence does this triple lie in
    subject: Entity
    predicate: Optional[Entity]
    object: Entity
    dependency_path: Optional[str]  # "lexicalized dependency path between sub and obj if exists" or None (if not existing)
    confidence: Optional[float]   # confidence of annotation if possible
    annotator: str  # annotator used to annotate this triple with the sentence


class Tweet(BaseModel):
    docid: str  # Document id     -- Wikipedia document id when dealing with wikipedia dump
    title: str  # title of the wikipedia document
    text: str  # The whole text of the document
    uri: str  # URI of the item containing the main page
    words_boundaries: List[List[int]]  # list of tuples (start, end) of each word in Wikipedia Article, start/ end are character indices
    sentences_boundaries: List[List[int]]  # start and end offsets of sentences :  [(start,end),(start,end)] start/ end are character indices
    triples: List[Triple]
    entities: List[Entity]
