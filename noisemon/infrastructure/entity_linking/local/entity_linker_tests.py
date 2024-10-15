import pytest
from noisemon.infrastructure.entity_linking.local.entity_linker import (
    EntityLinkerImpl,
    EntitySpan,
    EntityData,
)

# Initialize the EntityLinker for testing
entity_linker = EntityLinkerImpl()
entity_linker.initialize()


# Test cases
@pytest.mark.parametrize(
    "text, recognized_entities, ground_truth_qids",
    [
        pytest.param(
            "Apple Corp. is a tech company.",
            [EntitySpan("Apple Corp.", 0, 11)],
            [EntityData("Q312")],
            id="Test Case: Apple Corp.",
        ),
        pytest.param(
            "Facebook is a social media platform.",
            [EntitySpan("Facebook", 0, 8)],
            [EntityData("Q380")],
            id="Test Case: Facebook",
        ),
        pytest.param(
            "Google is a search engine.",
            [EntitySpan("Google", 0, 6)],
            [None],
            id="Test Case: Google (False Positive)",
        ),
        pytest.param(
            "This is a random sentence.",
            [],
            [],
            id="Test Case: Random Sentence (True Negative)",
        ),
    ],
)
def test_entity_linking_performance(text, recognized_entities, ground_truth_qids):
    # Perform entity linking
    entity_data = entity_linker.link_entities(text, recognized_entities)

    assert entity_data == ground_truth_qids
