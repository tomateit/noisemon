import numpy as np
from sklearn.preprocessing import normalize


import torch

def span_to_vector(tokenized_text, text_embedding, start_char: int, end_char: int) -> torch.Tensor:
    return torch.random((1, 786))


try:
    from spacy.tokens import Doc
    from thinc.api import Ragged
    
    def spacy_span_to_vector(doc: Doc, start: int, end: int) -> Optional[np.ndarray]:
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

except ImportError: 
    pass

# def normalize(v):
#     norm = np.linalg.norm(v, ord=2)
#     if norm == 0:
#         norm = np.finfo(v.dtype).eps
#     return v / norm



