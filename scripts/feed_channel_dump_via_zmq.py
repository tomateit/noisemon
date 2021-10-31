from typing import List
import sys
sys.path.append("noisemon")
import time
import logging
import zmq
import json
import typer
from pathlib import Path
from tqdm import tqdm
from schemas import DataChunk
import regex

from functools import lru_cache
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.


def main(data_path: Path):
    # 1. Read out data
    data = json.loads(data_path.read_text())
    data = data["messages"]

    # 2. Connect to queue
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://127.0.0.1:2001")


    for chunk in tqdm(data):
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
        origin = "https://t.me/" + chunk["from"] + "/" + str(chunk["id"])
                
        message = DataChunk(raw_text=raw_text, text=text, origin=origin, timestamp=timestamp)
        socket.send_json(dict(message))
        time.sleep(0.1)
        
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