from noisemon.logger import logger
from noisemon.domain.models.entity_span import EntitySpan

logger = logger.getChild(__name__)


class EntityRecognizer:
    def recognize_entities(self, text: str) -> list[EntitySpan]:
        ...
