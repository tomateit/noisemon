from enum import Enum

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers import pipeline

from noisemon.domain.models.entity_span import EntitySpan
from noisemon.domain.services.entity_recognition.entity_recognizer import EntityRecognizer
from noisemon.tools.span_to_vector import span_to_vector
from noisemon.tools.char_span_to_vector import ContextualEmbedding
from noisemon.logger import logger

logger = logger.getChild(__name__)


from pydantic import BaseModel

class HFEntity(BaseModel):
    entity_group: str
    score: float
    word: str
    start: int
    end: int


def hf_entity_to_entity_span(hf_entity: HFEntity) -> EntitySpan:
    return EntitySpan(
        span_start=hf_entity.start,
        span_end=hf_entity.end,
        span=hf_entity.word
    )


class EntityRecognizerLocalImpl(EntityRecognizer):
    def __init__(self, model_name="Jean-Baptiste/roberta-large-ner-english"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.nlp = pipeline('ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple")
        self.embedder = ContextualEmbedding(model_name=model_name)

    def recognize_entities(self, text):
        output = self.nlp(text)
        output: list[HFEntity] = [HFEntity(**e) for e in output]
        result = [hf_entity_to_entity_span(e) for e in output]
        return result



