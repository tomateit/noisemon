from typing import List

from tqdm import tqdm
from sqlalchemy import select

from noisemon.models import MentionModel
from noisemon.database.database import SessionLocal


def main():
    session = SessionLocal()

    with session.begin():
        query = select(MentionModel).where(MentionModel.vector_index >= 0).order_by(MentionModel.vector_index.asc())
        query_result = session.execute(query).scalars().all()

    index_to_entity_map = {int(x.vector_index): x for x in query_result}
    desired_index_order = list(range(len(query_result)))
    if sorted(index_to_entity_map.keys()) == desired_index_order:
        print("Vector Indices are fine, no need to reconcile")
        return

    with session.begin_nested():
        for _from, _to in tqdm(reconcile(list(index_to_entity_map.keys()))):
            entity = index_to_entity_map[_from]
            entity.vector_index = _to

    session.commit()
    print("Reconcilation is complete.")


def get_holes(indices: List[int]) -> List[int]:
    indices = indices.copy()
    list_of_holes = []
    desired_index = 0
    while indices:
        actual_index = indices.pop(0)
        while actual_index != desired_index:
            list_of_holes.append(desired_index)
            desired_index += 1
        desired_index += 1
    return list_of_holes


def reconcile(indices: List[int]):
    n = len(indices)
    desired_order = list(range(n))
    indices = sorted(indices.copy())
    map_ = {actual: actual for actual in (indices)}
    while sorted(map_.values()) != desired_order:
        last_key = indices.pop()
        for i in range(n):
            if i not in set(map_.values()):
                map_[last_key] = i
                break

    return [(key, value) for key, value in map_.items() if key != value]


if __name__ == "__main__":
    main()
