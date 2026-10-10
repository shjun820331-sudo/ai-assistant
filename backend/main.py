"""
나만의 AI 비서 - 백엔드 진입점

실행:  uvicorn main:app --reload
문서:  http://127.0.0.1:8000/docs
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.api_core.exceptions import GoogleAPICallError

from routers import chat, conversations, data

load_dotenv()

DEFAULT_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]

app = FastAPI(
    title="서울 기온 AI 비서 API",
    description="서울 월평균 기온 데이터를 이해하고 답하는 AI 비서의 백엔드",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.exception_handler(GoogleAPICallError)
def firestore_error(request: Request, exc: GoogleAPICallError):
    return JSONResponse(status_code=503, content={"detail": "데이터베이스에 연결하지 못했습니다. 잠시 후 다시 시도하세요."})


@app.get("/", tags=["상태"])
def health():
    """서버가 켜져 있는지 확인한다. (Render 무료 서버를 깨울 때도 사용)"""
    return {"status": "ok", "docs": "/docs"}
