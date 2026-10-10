"""conversations 컬렉션: 대화 기록 저장/조회/삭제"""
from datetime import datetime, timezone

from services.firestore import get_db

COLLECTION = "conversations"
TITLE_LENGTH = 30


def _collection():
    return get_db().collection(COLLECTION)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _overview(doc_id: str, doc: dict) -> dict:
    """목록용: messages 본문은 빼고 개수만 준다."""
    return {
        "id": doc_id,
        "title": doc["title"],
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
        "message_count": len(doc["messages"]),
    }


def create_conversation(messages: list[dict], title: str | None = None) -> dict:
    now = _now()
    doc = {
        "title": title or messages[0]["content"][:TITLE_LENGTH],
        "messages": messages,
        "created_at": now,
        "updated_at": now,
    }
    ref = _collection().document()
    ref.set(doc)
    return {"id": ref.id, **doc}


def list_conversations() -> list[dict]:
    docs = _collection().order_by("updated_at", direction="DESCENDING").stream()
    return [_overview(d.id, d.to_dict()) for d in docs]


def get_conversation(conversation_id: str) -> dict | None:
    snapshot = _collection().document(conversation_id).get()
    if not snapshot.exists:
        return None
    return {"id": snapshot.id, **snapshot.to_dict()}


def append_messages(conversation_id: str, new_messages: list[dict]) -> dict | None:
    conversation = get_conversation(conversation_id)
    if conversation is None:
        return None
    changes = {"messages": conversation["messages"] + new_messages, "updated_at": _now()}
    _collection().document(conversation_id).update(changes)
    return {**conversation, **changes}


def delete_conversation(conversation_id: str) -> bool:
    ref = _collection().document(conversation_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True
