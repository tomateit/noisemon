from abc import ABCMeta

from noisemon.domain.models.mention import MentionModel


class RDFConvertor(metaclass=ABCMeta):
    def convert_to_rdf(self, text: str, mentions: list[MentionModel]) -> list["Triplet"]:
        ...