"""
I do not want entities which are not of type ORG to be in the database
Because this limitation saves a lot of compute and allows to have more structured 'world'.
I do a prototype.
"""
from time import sleep

import typer
from SPARQLWrapper import SPARQLWrapper, JSON
from sqlalchemy import select
import sqlalchemy.sql.functions as func
from tqdm import tqdm

from noisemon.settings import settings
from noisemon.domain.models.entity import EntityModel
from noisemon.tools.retry_request import retry_request
from noisemon.tools.cache_to_redis import get_cacher
from noisemon.tools.tools import qid_from_uri
from noisemon.entity_recognizer import EntityType
from noisemon.database.database import SessionLocal
from noisemon.logger import logger

sparql = SPARQLWrapper("http://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)


redis_params = {
    "host": settings.REDIS_HOST,
    "port": settings.REDIS_PORT,
    "db": settings.REDIS_DB,
    "password": settings.REDIS_PASSWORD,
}
redis_cacher = get_cacher(redis_params, EXPIRE=60 * 60 * 24 * 7)
decorator = redis_cacher(key_argument_position=0)


@decorator
@retry_request
def check_entity(qid: str) -> bool:
    query = """
    SELECT ?orgLike WHERE {
        VALUES ?orgLike { 
            wd:Q93429702 
            wd:Q22687 
            wd:Q16691582 
            wd:Q4830453 
            wd:Q891723 
            wd:Q6881511
        }
        
        wd:%s wdt:P31 ?orgLike .
        
    } LIMIT 10 """ % (qid,)

    sparql.setQuery(query)
    results = sparql.query().convert()
    results = results["results"]["bindings"]
    return bool(results)


def main():
    db = SessionLocal()
    db.begin()
    count_statement = select(func.count(EntityModel.qid)).where(EntityModel.type == None)
    count = db.execute(count_statement).scalar()
    logger.info(f"Found {count} entities without type")
    statement = select(EntityModel).filter_by(type=None)
    statement = statement.execution_options(yield_per=1000)
    models = db.scalars(statement)

    with tqdm(total=count) as pbar:
        for entity_model in models:
            qid = qid_from_uri(entity_model.qid)
            with db.begin_nested():
                if check_entity(qid):
                    entity_model.type = EntityType.ORGANIZATION
                # else:
                #     db.delete(entity_model)
            db.flush()
            pbar.update(1)
            sleep(1)

    db.commit()
    db.close()


if __name__ == "__main__":
    typer.run(main)