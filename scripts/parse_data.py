import json
import typer
from pathlib import Path
from spacy.tokens import DocBin
from spacy.vocab import Vocab
from wasabi import Printer
import json
from pathlib import Path
from convert_labelstudio_to_spacy import LabelStudioToSpacyConverter
msg = Printer()
import os


def main(input_path: Path = typer.Option(None), output_folder: Path = typer.Option(None), most_recent: bool = typer.Option(False)):
    """Creating the corpus from the labelstudio annotations."""
    if most_recent and not input_path.is_dir():
        msg.fail("Incorrect arguments", "When `most_recent` flag, input_path shall be dir ")
        return
    assert output_folder.is_dir(), "`output_folder` must be a directory. I will be creating files there."
    if most_recent:
        files = list(input_path.glob("*.json"))
        if files:
            input_path = max(files, key=os.path.getctime)
        else:
            msg.fail(f"Directory {input_path} is empty")
            return
    
    msg.info(f"{input_path} is being processed.")
    data = json.loads(input_path.read_text())
    # Quite custom ....
    Vocab()

    # 1. Create NER Spacy Dataset
    output = []
    converter = LabelStudioToSpacyConverter()
    converter.ls_label_map = {
        ""
    }

    for labelstudio_line in data:
        doc = converter.create_spacy_doc(labelstudio_line)
        doc = converter.assign_entities(doc, labelstudio_line)
        output.append(doc)

    train_file = output_folder / "train.spacy"
    dev_file = output_folder / "dev.spacy"
    test_file = output_folder / "test.spacy"

    n_docs = len(output)
    seven_tenth = len(output)//10*7
    nine_tenth = len(output)//10*9
    msg.info(f"Processing finished. {n_docs}")

    docbin = DocBin(docs=output[:seven_tenth], store_user_data=True)
    docbin.to_disk(train_file)
    msg.good(f"Train set size: {len(docbin)}")
    msg.good(f"Saved to: {train_file}")

    docbin = DocBin(docs=output[seven_tenth:nine_tenth], store_user_data=True)
    docbin.to_disk(dev_file)
    msg.good(f"Dev set size: {len(docbin)}")
    msg.good(f"Saved to: {dev_file}")

    docbin = DocBin(docs=output[nine_tenth:], store_user_data=True)
    docbin.to_disk(test_file)
    msg.good(f"Test set size: {len(docbin)}")
    msg.good(f"Saved to: {test_file}")

    # 2. Create KB
    


if __name__ == "__main__":
    typer.run(main)
