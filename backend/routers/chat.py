"""AI 채팅 API"""
from fastapi import APIRouter, HTTPException, status
from openai import APIError

from schemas import ChatIn, ChatOut
from services import chat as chat_service

router = APIRouter(prefix="/api/chat", tags=["AI 채팅"])


@router.post("", response_model=ChatOut, summary="데이터 요약을 반영한 AI 답변 (대화 자동 저장)")
def chat(body: ChatIn):
    try:
        result = chat_service.chat(body.message, body.conversation_id)
    except chat_service.ChatConfigError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc))
    except APIError:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "AI 응답을 받지 못했습니다. 잠시 후 다시 시도하세요.")
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 id의 대화를 찾을 수 없습니다.")
    return result
