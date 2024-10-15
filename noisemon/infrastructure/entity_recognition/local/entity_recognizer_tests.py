import pytest

from noisemon.domain.services.entity_recognition.entity_recognizer import (
    EntityRecognizer,
)
from noisemon.infrastructure.entity_recognition.local.entity_recognizer import (
    EntityRecognizerLocalImpl,
)
from noisemon.domain.models.entity_span import EntitySpan
from noisemon.tools.similarity import similarity


@pytest.fixture
def entity_recognizer():
    return EntityRecognizerLocalImpl()


test_data = [
    pytest.param(
        "Apple Inc. is a leading tech company.",
        [
            EntitySpan(span="Apple Inc.", span_start=0, span_end=10),
        ],
        id="Test: 1 entity",
    ),
    pytest.param(
        "Apple Inc. is a leading tech company. Microsoft Corporation is also well-known.",
        [
            EntitySpan(span="Apple Inc.", span_start=0, span_end=10),
            EntitySpan(span="Microsoft Corporation", span_start=38, span_end=59),
        ],
        id="Test: 2 entities",
    ),
    pytest.param(
        "Amazon.com is an e-commerce giant. Google LLC is a tech company.",
        [
            EntitySpan(span="Amazon.com", span_start=0, span_end=10),
            EntitySpan(span="Google LLC", span_start=35, span_end=45),
        ],
        id="Test: 2 entities",
    ),
]


@pytest.mark.parametrize("text, true_entities", test_data)
def test_entity_recognition_count(text: str, true_entities, entity_recognizer):
    predicted_entities = entity_recognizer.recognize_entities(text)
    assert len(true_entities) == len(predicted_entities)


@pytest.mark.parametrize("text, true_entities", test_data)
def test_entity_partial_match(text: str, true_entities, entity_recognizer):
    predicted_entities = entity_recognizer.recognize_entities(text)
    threshold = 0.8
    for true, pred in zip(true_entities, predicted_entities, strict=True):
        assert threshold < similarity(true.span, [pred.span])


@pytest.mark.parametrize("text, true_entities", test_data)
def test_entity_recognition_full_match(text: str, true_entities, entity_recognizer):
    predicted_entities = entity_recognizer.recognize_entities(text)
    assert true_entities == predicted_entities


@pytest.mark.parametrize("text, true_entities", test_data)
def test_entity_recognition_span_index_consistency(
    text: str, true_entities, entity_recognizer
):
    predicted_entities = entity_recognizer.recognize_entities(text)
    for p in predicted_entities:
        assert p.span == text[p.span_start : p.span_end]


# def test_entity_recognition_partial_match_f1_score(text, true_entities, entity_recognizer):
# predicted_entities = entity_recognizer.recognize_entities(text)
# assert true_entities == predicted_entities
# Calculate and assert Partial Match F1 Score for each example
# partial_match_f1_score_1 = calculate_partial_match_f1_score(ground_truth_entities_1, predicted_entities_1)
# partial_match_f1_score_2 = calculate_partial_match_f1_score(ground_truth_entities_2, predicted_entities_2)


def test_class_initialization(entity_recognizer: EntityRecognizer):
    assert entity_recognizer is not None


def test_er_returns_non_empty_list(entity_recognizer: EntityRecognizer):
    sample = "Microsoft is a company."
    list_of_entity_spans = entity_recognizer.recognize_entities(sample)
    assert len(list_of_entity_spans) > 0
