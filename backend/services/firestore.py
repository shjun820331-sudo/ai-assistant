"""
Firestore 연결

서비스 계정 키는 코드에 넣지 않고 환경 변수에서 읽는다.
- FIREBASE_SERVICE_ACCOUNT_JSON : 키 JSON 내용 전체 (Render 배포용)
- FIREBASE_SERVICE_ACCOUNT_PATH : 키 파일 경로 (내 PC용)
"""
import json
import os
from functools import lru_cache
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")


def _credential() -> credentials.Certificate:
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        return credentials.Certificate(json.loads(raw))

    path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "").strip()
    if path:
        return credentials.Certificate(str(BACKEND_DIR / path))

    raise RuntimeError("Firebase 키가 없습니다. .env 에 FIREBASE_SERVICE_ACCOUNT_JSON 또는 _PATH 를 설정하세요.")


@lru_cache
def get_db():
    """Firestore 클라이언트를 한 번만 만들어 재사용한다."""
    if not firebase_admin._apps:
        firebase_admin.initialize_app(_credential())
    return firestore.client()
