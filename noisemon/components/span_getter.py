import spacy
from spacy.tokens import Span, Doc
import transformers
from transformers import AutoTokenizer
import spacy_alignments as tokenizations
from functools import partial as p
import spacy_transformers
from typing import Iterable, Callable, List
import numpy as np

@spacy.registry.span_getters("transformer_aware_strided_spans.v1")
def transformer_aware_strided_spans_configurator(tokenizer_name: str, window: int, stride: int) -> Callable:
    tokenizer_ = AutoTokenizer.from_pretrained(tokenizer_name)

    tokenizer = p(tokenizer_, padding=False, truncation=False)

    def transformer_aware_strided_spans(docs: Iterable[Doc]) -> List[List[Span]]:
        tokenized_texts = tokenizer([doc.text for doc in docs])
        sentencepieces = map(tokenizer_.convert_ids_to_tokens, tokenized_texts.input_ids)
        l_of_l_of_spans = []
        # print("-----", len(docs))
        for doc, sentencepiece in zip(docs, sentencepieces):
            _, b2a = tokenizations.get_alignments([token.text for token in doc], sentencepiece)
            b2a = [t for t in b2a if len(t)] # this will eliminate special tokens, so we shall be aware of length chage
            
    #         print(b2a, doc)
            if len(sentencepiece) < window:
                # docs too short are pushed as whole
                l_of_l_of_spans.append([doc[:]])
                continue
            buffer = []
            for i in range(0, len(sentencepiece), stride):
    #             print(i, window)
                sentencepice_window = b2a[i:i+window] # we always get the desired length of tokens ...
                # But: each partially included word will at the end splitted as it was whole
                # so, to have a little ease with that
                # drop last word at all if it's not whole
                last_word = sentencepice_window[-1]
                current = sentencepice_window.count(last_word)
                total = sentencepiece.count(last_word)
                if total != current:
                    sentencepice_window = sentencepice_window[:-current]

                sentencepice_window_flat = np.ndarray.flatten(np.array(sentencepice_window))
                if not len(sentencepice_window_flat):
                    continue
                min_ = sentencepice_window_flat.min().item()
                max_ = sentencepice_window_flat.max().item()
                span = doc[min_: max_ + 1]

                buffer.append(span)
            l_of_l_of_spans.append(buffer)



        return l_of_l_of_spans
    
    return transformer_aware_strided_spans