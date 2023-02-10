from enum import Enum

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers import pipeline

from noisemon.tools.span_to_vector import span_to_vector

class EntityType(str, Enum):
    ORGANIZATION = "ORG"


class EntityRecognizer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
        self.model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
        self.nlp = pipeline('ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple")


    def recognize_entities(self, text):
        result = self.nlp(text)
        # [{'entity_group': 'ORG',
        # 'score': 0.99381506,
        # 'word': ' Apple',
        # 'start': 0,
        # 'end': 5},
        return result

    def get_entity_vectors(self, text, recognized_entities):
        tokenized_text = self.tokenizer(text)
        text_embedding = self.model.head(tokenized_text)

        for entity in recognized_entities:
            start, end = entity["start"], entity["end"]
            entity_vector = span_to_vector(tokenized_text, text_embedding, start, end)
            entity["vector"]

        return recognized_entities

    def process(self, text) -> list[dict]:
        entities = self.recognize_entities(text)
        entities_with_vectors = self.get_entity_vectors(text, entities)
        return entities_with_vectors