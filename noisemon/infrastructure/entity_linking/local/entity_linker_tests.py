import pytest
from noisemon.infrastructure.entity_linking.local.entity_linker import EntityLinkerLocalImpl, EntitySpan, EntityData

# Initialize the EntityLinker for testing
entity_linker = EntityLinkerLocalImpl()
entity_linker.initialize()
# Test cases
@pytest.mark.parametrize(
    "text, recognized_entities, expected_f1, ground_truth_qids",
    [
        (
            "Apple Corp. is a tech company.",
            [EntitySpan("Apple Corp.", 0, 11)],
            1.0,
            [EntityData("Q312")],
        ),
        (
            "Facebook is a social media platform.",
            [EntitySpan("Facebook", 0, 8)],
            1.0,
            [EntityData("Q380")],
        ),
        (
            "Google is a search engine.",
            [EntitySpan("Google", 0, 6)],
            0.0,
            [None],
        ),
        (
            "This is a random sentence.",
            [],
            0.0,
            [],
        ),
    ],
    ids=[
        "Test Case: Apple Corp.",
        "Test Case: Facebook",
        "Test Case: Google (False Positive)",
        "Test Case: Random Sentence (True Negative)",
    ],
)
def test_entity_linking_performance(text, recognized_entities, expected_f1, ground_truth_qids):
    # Perform entity linking
    entity_data = entity_linker.link_entities(text, recognized_entities)

    # Compare with ground truth QIDs and calculate F1-score
    true_positive = 0
    for entity, ground_truth_qid in zip(entity_data, ground_truth_qids):
        if ground_truth_qid is None and entity is None:
            true_positive += 1
        elif ground_truth_qid is None or entity is None:
            continue
        elif entity.qid == ground_truth_qid.qid:
            true_positive += 1

    precision = true_positive / len(entity_data)
    recall = true_positive / len(recognized_entities)

    f1_score = 2 * (precision * recall) / (precision + recall)

    assert f1_score >= 0.8
