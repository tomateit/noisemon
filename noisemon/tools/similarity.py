from typing import Iterable
from difflib import SequenceMatcher


def similarity(A: str, Bs: Iterable[str]) -> float:
    """
    Calculates similarity between A and each of B, returns maximum
    """
    A = A.lower()
    return max([SequenceMatcher(None, A, B.lower()).ratio() for B in Bs])
