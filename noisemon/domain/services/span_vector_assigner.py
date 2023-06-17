from typing import Tuple, List, Iterable, Optional, Dict, Callable, Any

from spacy.tokens.doc import Doc
from spacy.tokens import Span
from wasabi import Printer
from spacy.language import Language
from spacy.tokens import Doc
import numpy as np
from thinc.api import Ragged
from sklearn.preprocessing import normalize

Span.set_extension("trf_vector", default=None, force=True)
msg = Printer()


@Language.component(
    "span_vector_assigner.v1",
    requires=["doc.ents", "doc._.trf_data"]
)
def span_vector_assigner_component(doc: Doc) -> Doc:
    d = 768
    try:
        d_ = doc._.trf_data.model_output[1].shape[1]
        if d_ != d:
            print(f"Expected dimension to be {d} but doc has {d_}")
        d = d_
    except Exception as ex:
        print(f"Error occured when checked dimension: {ex}")

    for entity in doc.ents:
        indices = doc._.trf_data.align[entity.start:entity.end].dataXd
        if not len(indices):
            continue

        document_tensor = doc._.trf_data.tensors[0]
        document_tensor = document_tensor.reshape(-1, d)
        vectors = document_tensor[indices]
        vector = normalize(vectors.mean(axis=0).reshape(1, -1))
        entity._.trf_vector = vector
    return doc



# def normalize(v):
#     norm = np.linalg.norm(v, ord=2)
#     if norm == 0:
#         norm = np.finfo(v.dtype).eps
#     return v / norm


def span_to_vector(doc: Doc, start: int, end: int) -> Optional[np.ndarray]:
    d = 768
    try:
        d_ = doc._.trf_data.model_output[1].shape[1]
        if d_ != d:
            print(f"Expected dimension to be {d} but doc has {d_}")
        d = d_
    except Exception as ex:
        print(f"Error occured when checked dimension: {ex}")

    indices = doc._.trf_data.align[start:end].dataXd
    if not len(indices):
        return None
    document_tensor = doc._.trf_data.tensors[0]
    document_tensor = document_tensor.reshape(-1, d)
    vectors = document_tensor[indices]
    vector = normalize(vectors.mean(axis=0).reshape(1, -1))
    return vector

