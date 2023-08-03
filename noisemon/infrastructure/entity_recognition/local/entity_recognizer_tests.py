import pytest

from noisemon.domain.services.entity_recognition.entity_recognizer import EntityRecognizer
from noisemon.infrastructure.entity_recognition.local.entity_recognizer import EntityRecognizerLocalImpl
from noisemon.domain.models.entity_span import EntitySpan
from noisemon.tools.metrics import calculate_partial_match_f1_score

@pytest.fixture
def entity_recognizer():
    return EntityRecognizerLocalImpl()

def test_entity_recognition_partial_match_f1_score(entity_recognizer):
    # Example 1: Input text and ground truth entities
    input_text_1 = "Apple Inc. is a leading tech company. Microsoft Corporation is also well-known."
    ground_truth_entities_1 = [
        EntitySpan(span="Apple Inc.", span_start=0, span_end=9),
        EntitySpan(span="Microsoft Corporation", span_start=44, span_end=63)
    ]
    predicted_entities_1 = entity_recognizer.recognize_entities(input_text_1)

    # Example 2: Input text and ground truth entities
    input_text_2 = "Amazon.com is an e-commerce giant. Google LLC is a tech company."
    ground_truth_entities_2 = [
        EntitySpan(span="Amazon.com", span_start=0, span_end=10),
        EntitySpan(span="Google LLC", span_start=37, span_end=47)
    ]
    predicted_entities_2 = entity_recognizer.recognize_entities(input_text_2)

    # Example 3: Add more test cases as needed
    # ...

    # Calculate and assert Partial Match F1 Score for each example
    partial_match_f1_score_1 = calculate_partial_match_f1_score(ground_truth_entities_1, predicted_entities_1)
    partial_match_f1_score_2 = calculate_partial_match_f1_score(ground_truth_entities_2, predicted_entities_2)

    assert partial_match_f1_score_1 > 0.95
    assert partial_match_f1_score_2 > 0.95


def test_class_initialization(entity_recognizer: EntityRecognizer):
    assert entity_recognizer is not None

def test_er_returns_non_empty_list(entity_recognizer: EntityRecognizer):
    sample = "Microsoft is a company."
    list_of_entity_spans = entity_recognizer.recognize_entities(sample)
    assert len(list_of_entity_spans) > 0
