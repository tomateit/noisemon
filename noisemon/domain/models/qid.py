import regex as re

class EntityQID:
    QID_PATTERN = re.compile(r"^Q\d+$")
    WIKIDATA_URL_PATTERN = re.compile(r"^https?://www.wikidata.org/(wiki|entity)/Q\d+$")

    def __init__(self, value):
        if not self.is_valid_qid(value):
            raise ValueError(f"Invalid Wikidata QID format: {value}")
        self.value = value

    def is_valid_qid(self, value):
        if self.QID_PATTERN.match(value):
            return True
        if self.WIKIDATA_URL_PATTERN.match(value):
            return True
        return False

    def __str__(self):
        # Normalize to the entity URL format
        return f"http://www.wikidata.org/entity/{self.get_qid()}"

    def get_qid(self):
        if self.is_valid_qid(self.value):
            # Extract QID from the URL
            return re.search(r"Q\d+", self.value).group()
        else:
            raise ValueError("Invalid Wikidata QID format")

