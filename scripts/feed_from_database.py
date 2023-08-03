import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve() / "noisemon"))
print(sys.path)

import typer
from pathlib import Path
from tqdm import tqdm
from models import Document
from database import SessionLocal

from processor import Processor


def main():
    # 1. Read out data
    db = SessionLocal()
    data = db.query(Document).order_by(Document.timestamp.desc()).limit(1000).all()

    processor = Processor()
    for document in tqdm(data):
        # message = DataChunk(link=document.link, raw_text=document.raw_text, text=document.text, timestamp=document.timestamp.isoformat())
        processor.process_data(document, transient=True)

        

if __name__ == "__main__":
    typer.run(main)