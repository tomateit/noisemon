import regex as re

class EntityQID:
    WIKIDATA_URL_PATTERN = re.compile(r'^https?://www.wikidata.org/(wiki|entity)/Q\d+$')

    def __init__(self, value):
        if not self.is_valid_qid(value):
            raise ValueError("Invalid Wikidata QID format")
        self.value = value

    def is_valid_qid(self, value):
        return bool(self.WIKIDATA_URL_PATTERN.match(value))

    def __str__(self):
        # Normalize to the entity URL format
        return f"https://www.wikidata.org/entity/{self.get_qid()}"

    def get_qid(self):
        if self.is_valid_qid(self.value):
            # Extract QID from the URL
            return re.search(r'Q\d+', self.value).group()
        else:
            raise ValueError("Invalid Wikidata QID format")

