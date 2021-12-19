from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve() / "noisemon"))
print(sys.path)
import time
import logging

import json
import typer
from pathlib import Path
from tqdm import tqdm
from schemas import DataChunk
import regex

from functools import lru_cache
from processor import Processor


def main(data_path: Path):
    # 1. Read out data
    data = json.loads(data_path.read_text())
    data = data["messages"]

    processor = Processor()

    # for chunk in tqdm(data[1000:2100]):
    for chunk in (data[2000:3100]):
        if chunk["type"] != "message": continue
        try:
            text = chunk['text']
            if type(text) == list:
                text = glue_chunks(text)
        except Exception as e:
            print(e)
            print(chunk)
            break
        raw_text = text
        timestamp = chunk["date"]
        link = "https://t.me/" + chunk["from"] + "/" + str(chunk["id"])
                
        message = DataChunk(raw_text=raw_text, text=text, link=link, timestamp=timestamp)
        # try:
        processor.process_data(message)
        # except Exception as ex:
        #     print(ex)
        time.sleep(0.5)
        
def glue_chunks(chunks: List)-> str:
    buffer = []
    for chunk in chunks:
        if type(chunk) == str:
            buffer.append(chunk)
        else:
            buffer.append(chunk["text"])
    buffer = " ".join(buffer)
    buffer = regex.sub(r"\s{2, }", " ", buffer)
    return buffer        

if __name__ == "__main__":
    typer.run(main)