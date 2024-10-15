import uuid

import uuid_utils
from tqdm import tqdm
from sqlalchemy import create_engine, text

from noisemon.settings import settings


def fill_document_id(conn_params):
    engine = create_engine(conn_params)


    try:
        with engine.connect() as conn:
            # Select rows with NULL document_id
            query = text(f"SELECT mention_id_str FROM mentions where mention_id is null;")
            result = list(conn.execute(query).scalars().all())
            update_query = text(f"UPDATE mentions SET mention_id = :new_document_id WHERE mention_id_str = :old_id ;")
            # Update rows with generated UUIDs
            buffer = []
            for old_id in tqdm(result):
                # print(old_id)
                new_document_id = uuid.UUID(str(uuid_utils.uuid7()))
                buffer.append({'new_document_id': new_document_id, 'old_id': old_id})
                if len(buffer) > 5000:
                    conn.execute(update_query, buffer)
                    buffer = []
                    conn.commit()
                    # break
            else:
                conn.execute(update_query, buffer)
                buffer = []
                conn.commit()


    except Exception as e:
        raise e

if __name__ == "__main__":
    fill_document_id(settings.DATABASE_URI)
