from abc import ABCMeta, abstractmethod

from noisemon.domain.models.language import LanguageCodes


class LanguageDetector(metaclass=ABCMeta):
    @abstractmethod
    def detect_language(self, text: str) -> LanguageCodes | None: ...
