from typing import List, Tuple, Callable
from transformers import AutoTokenizer, AutoModel
import spacy
from spacy.tokens import Doc, Span
from thinc.types import Floats2d, Ints1d, Ragged, cast
from thinc.api import Model, Linear, chain, Logistic
import torch

@spacy.registry.architectures("my_transformer_model.v1")
def create_transformer_model(
    get_spans,
    transformer_tokenizer: Model[List[str], List[Doc]],
    transformer_encoder: Model[List[Doc], List[Floats2d]],
) -> Model[List[Doc], Floats2d]:
    with Model.define_operators({">>": chain}):
        model = transformer_tokenizer >> transformer_encoder
    return model


@spacy.registry.architectures("my_transformer_encoder.v1")
def create_transformer_encoder_model(
    encoder_model_name: str
) -> Model[Floats2d, Floats2d]:
    
    model = AutoModel.from_pretrained(encoder_model_name)
    return Model(
        "transformer_encoder",
        encode_with_automodel,
        layers=[],
        refs={"encoder": model},
        init=instance_init,
    )

# @spacy.registry.architectures("my_transformer_embedder.v1")
# def create_transformer_embedder(
#     layer
# ) -> Model[Floats2d, Floats2d]:
    
#     model = AutoModel.from_pretrained(encoder_model_name)
#     return Model(
#         "transformer_encoder",
#         instance_forward,
#         layers=[tok2vec, pooling],
#         refs={"encoder": tokenizer, "pooling": pooling},
#         init=instance_init,
#     )

def encode_with_automodel(encoder_model: Model[List[Doc], List[Floats2d]], docs: List[Doc], is_train: bool) -> Tuple[Floats2d, Callable]:
    """
    This function creates 2d Tensors of Docs   
    """
    transformer_model = model.get_ref("encoder")
    # tokvecs, bp_tokvecs = tok2vec(docs, is_train)
    for doc_idx, doc in enumerate(docs):
        t = doc.bert_tokens
        with torch.no_grad():
            model_output = transformer_model(**{k: v.to(model.device) for k, v in t.items()})
        
        embeddings = model_output.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings)
        doc["tensor"] = embeddings[0].cpu().numpy()
        for i in range(1, len(t)):
            doc.spans[i-1]["vector"] = embeddings[i].cpu().numpy()

  
    def backprop(d_relations: Floats2d) -> List[Doc]:
        d_pooled = model.ops.reshape2f(d_relations, d_relations.shape[0] * 2, -1)
        # Apply pooling backprop callback
        d_ents = bp_pooled(d_pooled).data

        d_tokvecs = []
        ent_index = 0
        for doc_idx, list_of_pairs in enumerate(all_entity_combinations):
            # tokvecs contains sets of vecs for each token in doc
            shape = tokvecs[doc_idx].shape # (N Tokens x Emb Size)
            d_tokvec = model.ops.alloc2f(*shape)
            count_occ = model.ops.alloc2f(*shape)
            for entity_pair in list_of_pairs:
                for ent in entity_pair:
                    # Feedback all entities and the relation the were a part of
                    d_tokvec[ent.start : ent.end] += d_ents[ent_index]
                    count_occ[ent.start : ent.end] += 1
                    ent_index += ent.end - ent.start
            # Propagate the summary of that feedback back to the token level
            d_tokvec /= count_occ + 0.00000000001
            d_tokvecs.append(d_tokvec)

        d_docs = bp_tokvecs(d_tokvecs)
        return d_docs

    return relations, backprop

@spacy.registry.architectures("my_transformer_tokenizer.v1")
def create_transformer_tokenizer(
    tokenizer_model_name: str,
    # padding: bool = False,
    # truncation: bool = True
) -> Model[List[str], List[Doc]]:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_name)
    return Model(
        "transformer_tokenizer",
        tokenize_with_autotokenizer,
        layers=[],
        refs={"tokenizer": tokenizer},
        init=instance_init,
    )


def tokenize_with_autotokenizer(tokenizer: Model[List[str], List[Doc]], texts: List[str]) -> Doc:
    
    for text in texts:
        tokens = tokenizer(text, padding=False, truncation=False, return_tensors='pt')





def instance_init(model: Model, X: List[Doc] = None, Y: Floats2d = None) -> Model:
    # tok2vec = model.get_ref("tok2vec")
    # if X is not None:
    #     tok2vec.initialize(X)
    return model