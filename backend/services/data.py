"""data 컬렉션 CRUD"""
from schemas import DataIn
from services.firestore import get_db
from services.summary import summarize

COLLECTION = "data"


def _collection():
    return get_db().collection(COLLECTION)


def _to_doc(item: DataIn) -> dict:
    return {"date": item.date.isoformat(), "value": item.value, "memo": item.memo}


def list_data() -> list[dict]:
    docs = _collection().order_by("date").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


def create_data(item: DataIn) -> dict:
    ref = _collection().document()
    ref.set(_to_doc(item))
    return {"id": ref.id, **_to_doc(item)}


def update_data(data_id: str, item: DataIn) -> dict | None:
    ref = _collection().document(data_id)
    if not ref.get().exists:
        return None
    ref.set(_to_doc(item))
    return {"id": data_id, **_to_doc(item)}


def delete_data(data_id: str) -> bool:
    ref = _collection().document(data_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def get_summary() -> dict:
    return summarize(list_data())
