from pathlib import Path

import typer
import orjson
from tqdm import tqdm

from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import LinkedMentionData
from noisemon.infrastructure.repository_postgres.repository import RepositoryPostgresImpl
from noisemon.logger import logger
from noisemon.schemas.schemas import DatasetSchema, DatasetRowSchema, MentionSchema
from noisemon.settings import Settings

logger = logger.getChild("upload_dataset")


def main(dataset_path: Path):
    dataset_path = dataset_path.resolve()
    assert dataset_path.exists()
    logger.info(f"Uploading dataset from {dataset_path}")

    settings = Settings()
    database_uri = str(settings.DATABASE_URI)
    repository = RepositoryPostgresImpl(database_uri)
    logger.info("Instantiated repository")

    logger.info("Step 0: Reading-in and validating dataset.")
    dataset = orjson.loads(dataset_path.read_bytes())
    dataset = DatasetSchema.model_validate(dataset)
    logger.info("Step 0: Complete")

    logger.info("Step 1: Upsert Resource record")
    repository.persist_new_resource(dataset.resource.to_domain_model())
    logger.info("Step 1: Complete")

    logger.info("Step 2: Persisting entities")
    entities = set()
    for entry in dataset.entries:
        entry: DatasetRowSchema
        for mention in entry.mentions:
            mention: MentionSchema
            entities.add(mention.entity_qid)
    for entity_qid in tqdm(list(entities)):
        repository.persist_new_entity(EntityData(entity_qid=entity_qid, label=None, description=None))
    logger.info("Step 2: Complete")

    persisted_resource_links = []
    logger.info("Step 3: Persisting resource links")
    for entry in tqdm(dataset.entries):
        resource_link = entry.resource_link.to_domain_model()
        persisted_resource_link = repository.persist_new_resource_link(resource_link)
        persisted_resource_links.append(persisted_resource_link)
    logger.info("Step 3: Complete")



    logger.info("Step 4: Persisting documents and mentions")
    for entry, persisted_link in zip(tqdm(dataset.entries), persisted_resource_links, strict=True):
        entry: DatasetRowSchema
        document = entry.document.to_domain_model()
        persisted_document = repository.persist_new_document(document, persisted_link)
        for mention in entry.mentions:
            mention: MentionSchema
            mention: LinkedMentionData = mention.to_domain_model()
            repository.persist_new_mention(mention, persisted_document)
    logger.info("Step 4: Complete")

    logger.info(f"Successfully added {len(dataset.entries)} in the database")

if __name__ == "__main__":
    typer.run(main)

