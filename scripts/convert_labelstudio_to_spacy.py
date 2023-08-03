import spacy

from spacy.tokens import Doc
from wasabi import Printer
from typing import List, Callable, Dict
from pydantic import BaseModel
import scipy.special
msg = Printer()





class LabelStudioAnnotation(BaseModel):
    id: int
    completed_by: Dict
    result: List
    # {'value': {'start': 0,
    #   'end': 17,
    #   'text': 'ООО «Венера-плюс»',
    #   'labels': ['Organization']},
    #  'id': 'BDbfvhbqc9',
    #  'from_name': 'label',
    #  'to_name': 'text',
    #  'type': 'labels'},
    # {'value': {'start': 350,
    #   'end': 360,
    #   'text': '"Заказчик"',
    #   'labels': ['Role']},
    #  'id': 'ytWWFWYrvX',
    #  'from_name': 'label',
    #  'to_name': 'text',
    #  'type': 'labels'},
    # {'from_id': 'BDbfvhbqc9',
    #  'to_id': '8WJgOdX7zR',
    #  'type': 'relation',
    #  'direction': 'right',
    #  'labels': []},


class LabelStudioResult(BaseModel):
    data: Dict[str, str]
    annotations: List[LabelStudioAnnotation]
    meta: Dict
    created_at: str
    updated_at: str
    project: int
    file_upload: str
    predictions: List

class LabelStudioToSpacyConverter():
    ls_data_key = "text"
    ls_label_map = {"Organization": "ORG"}

    def __init__(self,
        nlp,
        extensions: List[str]=["rel", "trf_data"],
        preprocessor: Callable[[str], str] = None
        ):
        self.nlp = nlp
        self.preprocessor = preprocessor
        for extension in extensions:
            Doc.set_extension(extension, default={}, force=True)


    def create_spacy_doc(self, labelstudio: LabelStudioResult) -> spacy.tokens.Doc:
        text = labelstudio["data"][self.ls_data_key]
        if self.preprocessor:
            text = self.preprocessor(text)
        doc = self.nlp(text)
        return doc
        
    def assign_entities(self, doc: Doc, labelstudio) -> spacy.tokens.Doc:
        annotation = labelstudio["annotations"]
        entities = []
        for result in annotation[0]["result"]:
    #         print(result)
            if result["type"] == "labels":
                try:
                    
                    entity = doc.char_span(
                        result["value"]["start"], 
                        result["value"]["end"], 
                        label=self.ls_label_map[result["value"]["labels"][0]]
                    )
                    assert entity, "Entity failed to be created. Probably misaligned markup"
                    entities.append(entity)
                except:
                    msg.fail("REsult:", result)
                    msg.fail("Entity:", entity)
                    msg.fail("Doc:", doc)
                    msg.fail("----------")
        doc.ents = entities
        return doc

    def assign_entity_relations(self, doc: Doc, labelstudio) -> spacy.tokens.Doc:
        # ensure doc already has ents
        assert doc.ents, "Doc does not contain any entities assigned. Call `assign_entities` first"
        annotation = labelstudio["annotations"]
        rels = {}
        map_from_id_to_span = {} # {id: entity.start}
        # STEP 1 : to create all relations we must knwo whole labeling data as long as rels labeling refers to ner labeling
        for result in annotation[0]["result"]:
            if result["type"] == "labels":
                entity = doc.char_span(result["value"]["start"], result["value"]["end"])
                map_from_id_to_span[result["id"]] = entity.start
                
        # 1. Fill everything with negative examples
        for entity1 in doc.ents:
            for entity2 in doc.ents:
                if entity1 != entity2:
                    rels[(entity1.start, entity2.start)] = {"HAS_ROLE": 0.0}
            
        for result in annotation[0]["result"]:
            if result["type"] == "relation":
                # 2. Add positive examples
                from_id, to_id = result["from_id"], result["to_id"]
                span1 = map_from_id_to_span[from_id]
                span2 = map_from_id_to_span[to_id]
                rels[(span1, span2)] = {"HAS_ROLE": 1.0}
        
        assert len(rels) == (scipy.special.comb(len(doc.ents), 2) * 2), f"N of relations shall be n_ents*(n_ents-1): n_ents={len(doc.ents)}, n_rels={len(rels)}"

        doc._.rel = rels
        return doc


    

if __name__ == "__main__":
    typer.run(main)