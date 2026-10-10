"""
대화 기록 API

목록(GET /api/conversations)은 messages 본문 없이 개요만 주고,
대화 불러오기는 GET /api/conversations/{id} 로 전체 messages를 받는다.
"""
from fastapi import APIRouter, HTTPException, status

from schemas import ConversationIn, ConversationOut, ConversationOverview
from services import conversations as conversation_service

router = APIRouter(prefix="/api/conversations", tags=["대화 기록"])

NOT_FOUND = "해당 id의 대화를 찾을 수 없습니다."


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED, summary="대화 저장")
def create_conversation(body: ConversationIn):
    messages = [m.model_dump() for m in body.messages]
    return conversation_service.create_conversation(messages, body.title)


@router.get("", response_model=list[ConversationOverview], summary="대화 목록 조회 (최근순, messages 제외)")
def list_conversations():
    return conversation_service.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationOut, summary="대화 불러오기 (전체 messages)")
def get_conversation(conversation_id: str):
    conversation = conversation_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="대화 삭제")
def delete_conversation(conversation_id: str):
    if not conversation_service.delete_conversation(conversation_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
