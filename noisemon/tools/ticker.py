from typing import List

import regex
import reticker


class TickerProcessor:
    """
    Class extracts tickers from texts
    """

    explicit_dollarsign_ticker = regex.compile(r"(?<=\$)[A-Z]{1,5}")
    some_latin_uppers = regex.compile("[A-Z]{2,5}")

    def __init__(self):
        self.extractor = reticker.TickerExtractor()

    def extract_tickers(self, text: str) -> List[str]:
        """
        Takes a text, returns a list of strigs, that appear like tickers
        Just simple regex extraction
        """
        ticker_set = set(
            [
                *self.explicit_dollarsign_ticker.findall(text),
                *self.some_latin_uppers.findall(text),
            ]
        )

        return list(ticker_set)
