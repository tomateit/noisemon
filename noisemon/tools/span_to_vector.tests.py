import spacy
from spacy.tokens import Doc
from thinc.api import Ragged
from pathlib import Path
from sklearn.preprocessing import normalize
from span_to_vector import span_to_vector

root_dir = Path(__file__).parent.parent.parent
model_path = (root_dir / "training/nlp_trf-2.0.0/model-best").resolve()

nlp = spacy.load(model_path)
doc = nlp("Газпром выполняет свои обязательства и не влияет на рост цен на газ, говорят в Германии, "*20)

a = normalize(doc._.trf_data.tensors[0].reshape((-1,768))[[364,418]].mean(axis=0).reshape(1,-1))
b = normalize(doc._.trf_data.tensors[0].reshape(-1,768)[[381,435]].mean(axis=0).reshape(1,-1))
print(a.dot(b.T))
c = span_to_vector(doc, 272, 273)

print(a.dot(c.T))
assert a.dot(c.T) == a.dot(b.T), "Your code sucks"