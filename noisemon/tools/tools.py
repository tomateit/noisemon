from typing import List
from collections import Counter


def get_majority_by(candidates: List, field: str):
    """
    Returns the leftmost candidate with most frequent field value and its respective count (Nones ignored)
    """
    qids = [getattr(c, field) for c in candidates if c is not None]
    QID, count = Counter(qids).most_common(1)[0]
    for c in candidates:
        if c is not None and getattr(c, field) == QID:
            return c, count
    raise Exception("WTF")


def qid_from_uri(uri: str) -> str:
    qid = uri[uri.index("Q"):]
    return qid
