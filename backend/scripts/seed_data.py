"""
준비한 100개 데이터를 Firestore data 컬렉션에 넣기

실행(backend 폴더에서):  python -m scripts.seed_data
문서 id를 날짜로 쓰기 때문에 여러 번 실행해도 중복되지 않는다.
"""
import json
from pathlib import Path

from services.data import COLLECTION
from services.firestore import get_db

SOURCE = Path(__file__).resolve().parent.parent / "data" / "seoul_monthly_100.json"


def main():
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    db = get_db()
    batch = db.batch()
    for record in records:
        batch.set(db.collection(COLLECTION).document(record["date"]), record)
    batch.commit()
    print(f"적재 완료: {COLLECTION} 컬렉션에 {len(records)}개")


if __name__ == "__main__":
    main()
