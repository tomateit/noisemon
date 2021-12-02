from typing import Tuple, List, Iterable, Optional, Dict, Callable, Any

from spacy.tokens.doc import Doc
from wasabi import Printer
from spacy import Language

Doc.set_extension("rel", default={}, force=True)
msg = Printer()


@Language.component(
    "rel_ruler.v1",
    requires=["doc.ents"]
)
def my_component(doc: Doc) -> Doc:
    actual = tuple((x.label_ for x in doc.ents))
    pattern = ("ORG", "ROLE", "ORG", "ROLE")
    if actual == pattern:
        span1, span2, span3, span4 = [x.start for x in doc.ents]
        correct_arrangement = {
            (span1, span2): {"HAS_ROLE": 1.0},
            (span3, span4): {"HAS_ROLE": 1.0},
        }
        doc._.rel.update(correct_arrangement)
        return doc

    pattern = ("ORG", "ROLE", "PER", "ORG", "ROLE", "PER")
    if actual == pattern:
        span1, span2, _, span3, span4, _ = [x.start for x in doc.ents]
        correct_arrangement = {
            (span1, span2): {"HAS_ROLE": 1.0},
            (span3, span4): {"HAS_ROLE": 1.0},
        }
        doc._.rel.update(correct_arrangement)
        return doc
    return doc



