import spacy
from spacy.tokens import Doc
from thinc.api import Ragged
from pathlib import Path
from sklearn.preprocessing import normalize
from span_to_vector import span_to_vector
# from unittest import TestCase

root_dir = Path(__file__).parent.parent.parent
model_path = (root_dir / "training/nlp_trf-2.0.0/model-best").resolve()

nlp = spacy.load(model_path)
doc = nlp("Газпром выполняет 🤑 свои обязательства ❤, и  не влияет на рост цен на газ 🤑, говорят в Германии, "*20)

for entity in doc.ents:
    indices = doc._.trf_data.align[entity.start:entity.end].dataXd
    sliced = doc._.trf_data.tensors[0].reshape((-1,768))[indices]
    unified = sliced.mean(axis=0).reshape(1,-1)
    a = normalize(unified)
    b = span_to_vector(doc, entity.start, entity.end)
    difference = abs(1 - a.dot(b.T))
    assert difference < 0.0001, f"Your code sucks {difference}"

