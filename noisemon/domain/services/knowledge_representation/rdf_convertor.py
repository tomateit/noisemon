from abc import ABCMeta

from noisemon.domain.models.mention import MentionData
from noisemon.domain.models.statement import Statement


class RDFConvertor(metaclass=ABCMeta):
    def convert_to_rdf(self, text: str, mentions: list[MentionData]) -> list[Statement]:
        ...
