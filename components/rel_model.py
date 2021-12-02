from typing import List, Tuple, Callable

import spacy
from spacy.tokens import Doc, Span
from thinc.types import Floats2d, Ints1d, Ragged, cast
from thinc.api import Model, Linear, chain, Logistic, Relu, Dropout


@spacy.registry.architectures("rel_model.v1")
def create_relation_model(
    create_tensor_of_instance_combinations: Model[List[Doc], Floats2d],
    classification_layer: Model[Floats2d, Floats2d],
) -> Model[List[Doc], Floats2d]:
    with Model.define_operators({">>": chain}):
        model = create_tensor_of_instance_combinations >> classification_layer
        model.attrs["get_entity_combinations"] = create_tensor_of_instance_combinations.attrs["get_entity_combinations"]
    return model


@spacy.registry.architectures("rel_classification_layer.v1")
def create_classification_layer(
    nO: int = None, nI: int = None, dropout_ratio: float = 0.2
) -> Model[Floats2d, Floats2d]:
    # nI - input vector size
    # nO - output vector size
    with Model.define_operators({">>": chain}):
        return Relu(nI=nI, nO=nO, dropout=dropout_ratio) >> Linear(nI=nO, nO=None) >> Logistic()


@spacy.registry.misc("rel_create_entity_combinations.v1")
def create_entity_combinations(max_length: int) -> Callable[[Doc], List[Tuple[Span, Span]]]:
    def get_entity_combinations(doc: Doc) -> List[Tuple[Span, Span]]:
        """
        Get all possible instance combinations to score their relationships
        """
        instances = []
        for ent1 in doc.ents:
            for ent2 in doc.ents:
                if ent1 != ent2:
                    instances.append((ent1, ent2))
        return instances

    return get_entity_combinations


@spacy.registry.architectures("rel_create_tensor_of_instance_combinations.v1")
def create_tensor_of_instance_combinations(
    tok2vec: Model[List[Doc], List[Floats2d]],
    pooling: Model[Ragged, Floats2d],
    get_entity_combinations: Callable[[Doc], List[Tuple[Span, Span]]],
) -> Model[List[Doc], Floats2d]:

    return Model(
        "instance_tensors",
        instance_forward,
        layers=[tok2vec, pooling],
        refs={"tok2vec": tok2vec, "pooling": pooling},
        attrs={"get_entity_combinations": get_entity_combinations},
        init=instance_init,
    )


def instance_forward(model: Model[List[Doc], Floats2d], docs: List[Doc], is_train: bool) -> Tuple[Floats2d, Callable]:
    """
    This function creates 2d Tensors of entity pairs    
    """
    pooling = model.get_ref("pooling")
    tok2vec = model.get_ref("tok2vec")
    get_entity_combinations = model.attrs["get_entity_combinations"] # [(span, span)]
    all_entity_combinations: List[List[Tuple[Span, Span]]] = [get_entity_combinations(doc) for doc in docs] # [[(span, span)]]
    tokvecs, bp_tokvecs = tok2vec(docs, is_train)

    ents = [] # [[int]] token vectors of entities
    lengths = [] # [int] respectable length of entity spans

    for doc_idx, (list_of_pairs, tokvec) in enumerate(zip(all_entity_combinations, tokvecs)):
        token_indices = [] # inicies of entity tokens

        for entity_pair in list_of_pairs:
            for ent in entity_pair:
                token_indices.extend([i for i in range(ent.start, ent.end)])
                lengths.append(ent.end - ent.start)

        ents.append(tokvec[token_indices])

    # if not ents:
    #     return None, lambda x: []
    # ensure list of lengths is of the correct size
    lengths = cast(Ints1d, model.ops.asarray(lengths, dtype="int32"))
    # The Ragged dataclass represents a concatenated batch of sequences. 
    # An auxiliary array is used to keep track of the lengths.
    entities = Ragged(model.ops.flatten(ents), lengths)

    # pooling is just averaging the return is matrix of (len(length), embeddingSize)
    pooled, bp_pooled = pooling(entities, is_train)

    # as long as we stored each entity pair one by one, then we can
    # Reshape so that pairs of rows are concatenated like one candidate relation per row
    relations: Floats2d = model.ops.reshape2f(pooled, -1, pooled.shape[1] * 2) # [Float2d]

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


def instance_init(model: Model, X: List[Doc] = None, Y: Floats2d = None) -> Model:
    tok2vec = model.get_ref("tok2vec")
    if X is not None:
        tok2vec.initialize(X)
    return model
