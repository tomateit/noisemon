from itertools import islice
from typing import Tuple, List, Iterable, Optional, Dict, Callable, Any

from spacy.scorer import PRFScore
from thinc.types import Floats2d
import numpy
from spacy.training.example import Example
from thinc.api import Model, Optimizer
from spacy.tokens.doc import Doc
from spacy.pipeline.trainable_pipe import TrainablePipe
from spacy.vocab import Vocab
from spacy import Language
from thinc.model import set_dropout_rate
from wasabi import Printer


Doc.set_extension("rel", default={}, force=True)
msg = Printer()


@Language.factory(
    "relation_extractor",
    requires=["doc.ents", "token.ent_iob", "token.ent_type"],
    assigns=["doc._.rel"],
    default_score_weights={
        "rel_micro_p": None,
        "rel_micro_r": None,
        "rel_micro_f": None,
    },
)
def make_relation_extractor(
    nlp: Language, name: str, model: Model, *, threshold: float
):
    """Construct a RelationExtractor component."""
    return RelationExtractor(nlp.vocab, model, name, threshold=threshold)


class RelationExtractor(TrainablePipe):
    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "rel",
        *,
        threshold: float,
    ) -> None:
        """Initialize a relation extractor."""
        self.vocab = vocab
        self.model = model # thinc model from rel_model Model[List[Doc], List[Floats2d]]
        self.name = name
        self.cfg = {"labels": [], "threshold": threshold}

    @property
    def labels(self) -> Tuple[str]:
        """Returns the labels currently added to the component."""
        return tuple(self.cfg["labels"])

    @property
    def threshold(self) -> float:
        """Returns the threshold above which a prediction is seen as 'True'."""
        return self.cfg["threshold"]

    def add_label(self, label: str) -> int:
        """Add a new label to the pipe."""
        if not isinstance(label, str):
            raise ValueError("Only strings can be added as labels to the RelationExtractor")
        if label in self.labels:
            return 0
        self.cfg["labels"] = list(self.labels) + [label]
        return 1

    def __call__(self, doc: Doc) -> Doc:
        """Apply the pipe to a Doc."""
        # check that there are actually any candidate instances in this batch of examples
        number_of_entity_combinations = len(self.model.attrs["get_entity_combinations"](doc))
        if number_of_entity_combinations == 0:
            msg.info("[self.call] Could not determine any entity combination in doc - returning doc as is.")
            return doc

        predictions = self.predict([doc])
        self.set_annotations([doc], predictions)
        return doc

    def predict(self, docs: Iterable[Doc]) -> Floats2d:
        """Apply the pipeline's model to a batch of docs, without modifying them."""
        get_entity_combinations = self.model.attrs["get_entity_combinations"]
        number_of_entity_combinations = sum([len(get_entity_combinations(doc)) for doc in docs])
        if number_of_entity_combinations == 0:
            # msg.info("[self.predict] Could not determine any instances in any docs - can not make any predictions.")
            return [[]]
        scores = self.model.predict(docs)
        return self.model.ops.asarray(scores)

    def set_annotations(self, docs: Iterable[Doc], scores: Floats2d) -> None:
        """Modify a batch of `Doc` objects, using pre-computed scores."""
        c = 0
        get_entity_combinations = self.model.attrs["get_entity_combinations"]
        for doc in docs:
            for (e1, e2) in get_entity_combinations(doc):
                offset = (e1.start, e2.start)
                if offset not in doc._.rel:
                    doc._.rel[offset] = {}
                for j, label in enumerate(self.labels):
                    doc._.rel[offset][label] = scores[c, j]
                c += 1

    def update(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        set_annotations: bool = False,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model. Delegates to predict and get_loss."""
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        set_dropout_rate(self.model, drop)

        # check that there are actually any candidate instances in this batch of examples
        total_instances = 0
        for eg in examples:
            total_instances += len(self.model.attrs["get_entity_combinations"](eg.predicted))
        if total_instances == 0:
            # msg.info("[self.update] Could not determine any instances in doc, return losses as {}.")
            return losses

        # run the model
        docs = [eg.predicted for eg in examples]
        predictions, backprop = self.model.begin_update(docs)
        loss, gradient = self.get_loss(examples, predictions)
        backprop(gradient)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses[self.name] += loss
        if set_annotations:
            self.set_annotations(docs, predictions)
        return losses

    def get_loss(self, examples: Iterable[Example], scores) -> Tuple[float, float]:
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores."""
        truths = self._examples_to_truth(examples)
        gradient = scores - truths
        mean_square_error = (gradient ** 2).sum(axis=1).mean()
        return float(mean_square_error), gradient

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Language = None,
        labels: Optional[List[str]] = None,
    ):
        """Initialize the pipe for training, using a representative set
        of data examples.
        """
        if labels is not None:
            for label in labels:
                self.add_label(label)
        else:
            for example in get_examples():
                relations = example.reference._.rel
                for indices, label_dict in relations.items():
                    for label in label_dict.keys():
                        self.add_label(label)
        self._require_labels()

        subbatch = list(islice(get_examples(), 10))
        doc_sample = [eg.reference for eg in subbatch]
        label_sample = self._examples_to_truth(subbatch)
        if label_sample is None:
            raise ValueError("Call begin_training with relevant entities and relations annotated in "
                             "at least a few reference examples!")
        self.model.initialize(X=doc_sample, Y=label_sample)

    def _examples_to_truth(self, examples: List[Example]) -> Optional[numpy.ndarray]:
        # check that there are actually any candidate instances in this batch of examples
        nr_instances = 0
        for eg in examples:
            nr_instances += len(self.model.attrs["get_entity_combinations"](eg.reference))
        if nr_instances == 0:
            msg.info(f"[self._examples_to_truth] None of the references contain any of entities ")
            return None

        truths = numpy.zeros((nr_instances, len(self.labels)), dtype="f")
        c = 0
        for i, eg in enumerate(examples):
            for (e1, e2) in self.model.attrs["get_entity_combinations"](eg.reference):
                gold_label_dict = eg.reference._.rel.get((e1.start, e2.start), {})
                for j, label in enumerate(self.labels):
                    truths[c, j] = gold_label_dict.get(label, 0)
                c += 1

        truths = self.model.ops.asarray(truths)
        return truths

    def score(self, examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
        """Score a batch of examples."""
        return score_relations(examples, self.threshold)


def score_relations(examples: Iterable[Example], threshold: float) -> Dict[str, Any]:
    """Score a batch of examples."""
    # msg.info("Scoring is invoked, Threshold: ", threshold)
    micro_prf = PRFScore()
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    incorrect_span = 0
    for example in examples:
        gold = example.reference._.rel
        pred = example.predicted._.rel
        
        if not(len(gold)):
            print(example.reference)
        assert len(gold), "Missing labeling"
        # if set(pred.keys()) != (set(gold.keys())):
        #     print("Alien keys: ", set(pred.keys()).difference(set(gold.keys())))
        #     print("Predicted: ", pred.keys())
        #     print("Gold: ", gold.keys())
        for predicted_span, predicted_labels_with_probability in pred.items():
            if predicted_span not in gold:
                incorrect_span += 1
                # incorrectly recognized do not present in gold
                # raise Exception("WTF " + str(predicted_span))
                continue
            gold_labels = [true_label for (true_label, true_label_prob) in gold[predicted_span].items() if true_label_prob == 1.0]
            for predicted_label, predicted_label_probability in predicted_labels_with_probability.items():
                if predicted_label_probability >= threshold:
                    if predicted_label in gold_labels:
                        micro_prf.tp += 1
                        tp += 1
                    else:
                        micro_prf.fp += 1
                        fp += 1
                else:
                    if predicted_label in gold_labels:
                        micro_prf.fn += 1
                        fn += 1
                    else:
                        tn += 1
    # msg.info(f"Scoring is invoked, Threshold: {threshold}")
    # print("-----------")
    # print("Pair:\tGold score:\tPredicted score:\t")
    # assume gold and pred has the same order of keys
    # for gold_pair, gold_lable_to_score, pred_label_to_score in zip(gold.keys(),  gold.values(), pred.values()):
    #     print(str(gold_pair).ljust(10), gold_lable_to_score["HAS_ROLE"], pred_label_to_score["HAS_ROLE"], sep="\t")
    # print("Predicted: ", pred)
    # print("Gold: ", gold)
    # msg.info(f"TP: {tp} FP: {fp} TN: {tn} FN: {fn} Alien span: {incorrect_span}" )
    # print(micro_prf)
    return {
        "rel_tp": tp,
        "rel_fp": fp,
        "rel_tn": tn,
        "rel_fn": fn,
        "rel_alien_spans": incorrect_span,
        "rel_micro_p": micro_prf.precision,
        "rel_micro_r": micro_prf.recall,
        "rel_micro_f": micro_prf.fscore,
    }
