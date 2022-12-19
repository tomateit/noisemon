from typing import List, Dict, Optional

from spacy.tokens import Doc, Span

from noisemon.tools.ticker import TickerProcessor
from noisemon.logger import logger
from noisemon.models import EntityModel
from noisemon.database.wikidata import Wikidata

wikidata = Wikidata()
ticker_processor = TickerProcessor()


def ticker_strategy(doc: Doc, linked_entities) -> List[Optional[EntityModel]]:
    """
    Match tickers with entities, create new entities from matched, add new vectors
    """
    # Design decision: quit the function asap - avoid heavy calls
    logger.debug("Population with ticker strategy invoked")
    # 1. Extract entities
    recognized_entities: List[Span] = [ent for ent in doc.ents if
                                       ent.label_ == "ORG" and ent._.trf_vector is not None]
    assert len(recognized_entities) == len(linked_entities), "Inconsistent lengths"
    # 2.  Extract tickers
    tickers = ticker_processor.extract_tickers(doc.text)  # tickers are unique
    if not tickers:
        logger.debug(f"No tickers detected. Quitting the strategy")
        return []
    logger.debug(f"Detected Tickers: {tickers}")

    # 3. Match entities and tickers
    # For each ticker we find company with same ticker and get its aliases
    # We do not know which ticker belongs to which ORG at all,
    # So it's reasonable to perform lookup through all aliases
    possible_orgs: Dict[str, List[str]] = {}  # {QID : {set of aliases}}
    for ticker in tickers:
        lookup_result: Dict[str, List[str]] = wikidata.lookup_aliases_by_ticker(ticker)
        if lookup_result:
            possible_orgs.update(lookup_result)
    # this can erase some entities with overlapping aliases, but let it be so for now
    reverse_index = {
        alias.lower(): qid
        for qid, alias_set in possible_orgs.items()
        for alias in alias_set
    }

    organizations_matched = []

    for entity in recognized_entities:
        QID = None
        for key in reverse_index:
            if (key.lower() in entity.text.lower()) or (entity.text.lower() in key.lower()):
                QID = reverse_index[key]
                break
        organizations_matched.append(QID)
    assert len(recognized_entities) == len(organizations_matched), "Inconsistent lengths"

    logger.debug(f"Matched {sum(set([1 for i in organizations_matched if i]))} entities by ticker")

    newly_created_entities: List[Optional[EntityModel]] = []
    for idx, QID, recognized_entity, linked_entity in zip(range(len(recognized_entities)), organizations_matched,
                                                          recognized_entities, linked_entities):
        # basically 4 states:
        # {no QID}, {QID and LinkedEntity[may match or mismatch qids]}, and {QID + no LinkedEntity}
        if not QID:  # no QID
            # recognized entity does not resemble any of tickers' aliases
            logger.info(f"Recognized entity `{recognized_entity}` did not match any doc's tickers' aliases")
            newly_created_entities.append(None)
            continue
        elif QID and linked_entity:  # both exist
            if QID == linked_entity.qid:
                logger.info(
                    f"Recognized entity {recognized_entity} Linked as {linked_entity.name} got correct match with one of the doc tickers")
                newly_created_entities.append(None)
                continue
            else:
                # assuming that entity_linking capabilities prevail on alias comparasion
                # we do not create new entity based on alias matching
                logger.warning(
                    f"Matched already linked entity {linked_entity.name} recognized as {recognized_entity} by ticker aliases, but it matches {QID} alias instead")
                newly_created_entities.append(None)
                continue
        elif QID and not linked_entity:  # no linked entity
            if entity := EntityModel.get_by_qid(self.db, QID):
                # PERHAPS we already have such entity but did not match it, BC have not seen similar alias
                logger.debug(f"Entity {entity.name} is in database but was not linked with {recognized_entity}")
                newly_created_entities.append(entity)
                linked_entities[idx] = entity  # may not propagate long enough and be buggy
                continue
            else:
                # no such known entity in db, creation process
                name = wikidata.lookup_entity_label_by_qid(QID)
                # with self.db.begin_nested():
                #     entity = Entity(qid=QID, name=name, type=EntityType.ORGANIZATION)
                #     logger.info(f"Creating new entity: {QID} as {name}")
                #     self.db.add(entity)
                #     newly_created_entities.append(entity)
                # self.db.commit()
        else:
            raise Exception(
                f"Incorrect state, unsupported combination: {QID}, {recognized_entity}, {linked_entity}")

    return newly_created_entities
