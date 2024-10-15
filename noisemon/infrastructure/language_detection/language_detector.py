from noisemon.domain.models.language import LanguageCodes
from noisemon.domain.services.language_detection.language_detector import (
    LanguageDetector,
)
from lingua import Language, LanguageDetectorBuilder


class LanguageDetectorLocalImpl(LanguageDetector):
    def __init__(self):
        languages = [Language.ENGLISH, Language.RUSSIAN]
        self.detector = LanguageDetectorBuilder.from_languages(*languages).build()

    def detect_language(self, text: str) -> LanguageCodes | None:
        language = self.detector.detect_language_of(text=text)
        if not language:
            return None
        match language:
            case Language.RUSSIAN:
                return LanguageCodes.RU
            case Language.ENGLISH:
                return LanguageCodes.EN
            case _:
                return None
