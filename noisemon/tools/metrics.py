from typing import List
from noisemon.domain.models.entity_span import EntitySpanData


def calculate_partial_match_f1_score(
    ground_truth_entities: List[EntitySpanData], predicted_entities: List[EntitySpanData]
):
    # Convert ground truth and predicted entities to sets for faster lookup
    ground_truth_set = {
        (entity.span_start, entity.span_end): entity for entity in ground_truth_entities
    }
    {(entity.span_start, entity.span_end): entity for entity in predicted_entities}

    # Initialize counters for true positives, false positives, and false negatives
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    # Iterate over each predicted entity
    for pred_entity in predicted_entities:
        pred_start, pred_end = pred_entity.span_start, pred_entity.span_end

        # Check if there is an exact match in ground truth entities
        if (pred_start, pred_end) in ground_truth_set:
            true_positives += 1
        else:
            # Partial match check
            partial_match = False
            for gt_start, gt_end in ground_truth_set:
                if pred_start >= gt_start and pred_end <= gt_end:
                    partial_match = True
                    break

            if partial_match:
                true_positives += 1
            else:
                false_positives += 1

    # Calculate false negatives
    false_negatives = len(ground_truth_entities) - true_positives

    # Calculate precision, recall, and F1 score
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )
    f1_score = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return f1_score
