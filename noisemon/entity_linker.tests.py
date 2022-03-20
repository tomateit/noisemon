from entity_linker import EntityLinker
from pathlib import Path
import spacy
from spacy.tokens import Doc
from thinc.api import Ragged

root_dir = Path(__file__).parent.parent
model_path = (root_dir / "training/nlp_trf-2.0.0/model-best").resolve()
nlp = spacy.load(model_path)
article = (Path(__file__).parent / "test_assets/article.txt").resolve().read_text()
linker = EntityLinker()
doc = nlp(article)
print(linker.link_entities(doc))