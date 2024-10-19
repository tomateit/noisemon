import pytest
from noisemon.tools.metrics import calculate_partial_match_f1_score
from noisemon.domain.models.entity_span import EntitySpanData


@pytest.fixture
def ground_truth_entities():
    return [
        EntitySpanData(span="Google", span_start=0, span_end=5),
        EntitySpanData(span="Apple Inc.", span_start=10, span_end=20),
        EntitySpanData(span="Microsoft", span_start=25, span_end=34),
    ]


@pytest.fixture
def predicted_entities():
    return [
        EntitySpanData(span="Google", span_start=0, span_end=5),
        EntitySpanData(span="Apple", span_start=10, span_end=15),
        EntitySpanData(span="Facebook", span_start=18, span_end=26),
    ]


def test_partial_match_f1_score(ground_truth_entities, predicted_entities):
    f1_score = calculate_partial_match_f1_score(
        ground_truth_entities, predicted_entities
    )
    assert f1_score == pytest.approx(0.571, abs=1e-3)
