from spacy.cli.project.run import project_run
from spacy.cli.project.assets import project_assets
from pathlib import Path


def test_project():
    # root = Path(__file__).parent
    root = Path(__file__)
    project_assets(root)
    project_run(root, "download", capture=True)
    project_run(root, "training", capture=True)
