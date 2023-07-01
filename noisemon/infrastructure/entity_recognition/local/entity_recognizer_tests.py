import pytest
from noisemon.infrastructure.entity_recognition.local.entity_recognizer import EntityRecognizerLocalImpl


class TestEntityRecognizer:
    def setup_method(self):
        self.er = EntityRecognizerLocalImpl()

    def test_class_initialization(self):
        assert self.er is not None

    def test_er_returns_non_empty_list(self):
        sample = "Microsoft is a company."
        list_of_entity_spans = self.er.recognize_entities(sample)
        assert len(list_of_entity_spans) > 0
