import typer
from pathlib import Path

import spacy
from spacy.tokens import DocBin
from spacy.training import Example

# we need to import this to parse the custom reader from the config

from noisemon.entity_linker import EntityLinker

def main(nlp_dir: Path, test_set: Path):
    """ Evaluate the new Entity Linking component by applying it to unseen text. """
    nlp = spacy.util.load_model_from_path(nlp_dir)
    EntityLinker()
    
    examples = []
    doc_bin = DocBin().from_disk(test_set)
    docs = doc_bin.get_docs(nlp.vocab)
    for doc in docs:
        examples.append(Example(nlp(doc.text), doc))

    print()
    print("RESULTS ON THE TEST SET:")
    for example in examples:
        print(example.text)
        print(f"Gold annotation: {example.reference.ents[0].kb_id_}")
        print(f"Predicted annotation: {example.predicted.ents[0].kb_id_}")
        print()

    print()
    print("RUNNING THE PIPELINE ON UNSEEN TEXT:")
    text = "Русал предъявил иск газпрому"
    doc = nlp(text)
    print(text)
    for ent in doc.ents:
        print(ent.text, ent.label_, ent.kb_id_)
    print()



if __name__ == "__main__":
    typer.run(main)
