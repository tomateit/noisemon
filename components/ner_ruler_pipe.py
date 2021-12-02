from typing import Tuple, List, Iterable, Optional, Dict, Callable, Any

from spacy.tokens.doc import Doc
from wasabi import Printer
from spacy import Language
import regex as re


msg = Printer()


@Language.component(
    "ner_ruler.v1",
    assigns=["doc.ents"],
    requires=["doc.ents"],
)
def my_ner_ruler(doc: Doc) -> Doc:

    filtered_ents = []
    for entity in doc.ents:
        # PER cannot contain numbers
        if entity.label_ == "PER":
            if re.search("\d", entity.text):
                continue
        # I haven't met any actual entity with this oftenly mistaken word
        if "договор" in entity.text.lower():
            continue
        filtered_ents.append(entity)

    filtered_ents
    doc.ents = filtered_ents
    return doc



