from dataclasses import dataclass
from typing import Literal
from copy import deepcopy

from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers import pipeline

from noisemon.domain.models.entity_span import EntitySpan
from noisemon.domain.services.entity_recognition.entity_recognizer import EntityRecognizer
from noisemon.logger import logger

logger = logger.getChild(__name__)

@dataclass
class HFEntity:
    entity_group: Literal["MISC", "ORG", "PER", "LOC", "O"]
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


def merge_consecutive(data: list[HFEntity]):
    data = deepcopy(data)
    merged_data = []
    current_obj = None

    for obj in data:
        if current_obj is None:
            current_obj = obj
        elif obj.start == current_obj.end:
            current_obj.end = obj.end
            current_obj.word += obj.word
            current_obj.score = (current_obj.score + obj.score) / 2
        else:
            merged_data.append(current_obj)
            current_obj = obj

    if current_obj:
        merged_data.append(current_obj)

    return merged_data


def strip_whitespaces(datum: HFEntity, text: str) -> HFEntity:
    if datum.word.startswith(" "):
        datum = deepcopy(datum)
        word = datum.word[1:]
        start = text.index(
            word,
            max([datum.start - 2, 0]),
            datum.end + 2
        )
        end = start + len(word)

        datum = HFEntity(
            score=datum.score,
            entity_group=datum.entity_group,
            word=word,
            start=start,
            end=end,
        )

    return datum


class EntityRecognizerLocalImpl(EntityRecognizer):
    def __init__(self):
        model_name = "philschmid/distilroberta-base-ner-conll2003"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.nlp = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )

    def recognize_entities(self, text):
        output = self.nlp(text)
        output: list[HFEntity] = [HFEntity(**e) for e in output]
        output_merged = merge_consecutive(output)
        output_stripped = [strip_whitespaces(d, text=text) for d in output_merged]
        result = [hf_entity_to_entity_span(e) for e in output_stripped if e.entity_group == "ORG"]
        return result



