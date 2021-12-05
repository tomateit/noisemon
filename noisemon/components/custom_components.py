from functools import partial
from pathlib import Path
from typing import Iterable, Callable
import spacy
from spacy.training import Example
from spacy.tokens import DocBin, Doc
import spacy_transformers

from .span_vector_assigner import span_vector_assigner_component




