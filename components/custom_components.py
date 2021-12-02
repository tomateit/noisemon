from functools import partial
from pathlib import Path
from typing import Iterable, Callable
import spacy
from spacy.training import Example
from spacy.tokens import DocBin, Doc
import spacy_transformers

try:
    # make the factory work
    from components.rel_pipe import make_relation_extractor
    # make the config work
    from components.rel_model import create_relation_model, create_classification_layer, create_entity_combinations, create_tensor_of_instance_combinations

    from components.rel_ruler_pipe import *
    from components.span_getter import *
except ImportError:
    from rel_pipe import make_relation_extractor
    from rel_model import create_relation_model, create_classification_layer, create_entity_combinations, create_tensor_of_instance_combinations
    from rel_ruler_pipe import *
    from span_getter import *


