from noisemon.domain.models.mention import MentionModel
from noisemon.domain.services.information_representation.rdf_convertor import RDFConvertor


class RDFConvertorVendorImpl(RDFConvertor):
    def convert_to_rdf(self, text: str, mentions: list[MentionModel]) -> list["Triplet"]:
        ...