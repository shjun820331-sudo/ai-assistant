"""요청/응답 데이터 모양 (Pydantic 검증)"""
import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field


class DataIn(BaseModel):
    """데이터 추가/수정 요청"""
    date: dt.date = Field(examples=["2025-12-01"], description="날짜 (YYYY-MM-DD)")
    value: float = Field(ge=-90, le=60, allow_inf_nan=False, examples=[1.25], description="월평균 기온(℃)")
    memo: str = Field(default="", max_length=200, examples=["폭염일 3일"])


class DataOut(DataIn):
    id: str


class Metrics(BaseModel):
    average: float
    max: float
    max_date: dt.date
    min: float
    min_date: dt.date


class Summary(BaseModel):
    """AI 프롬프트에 주입하는 데이터 요약"""
    period: str | None
    count: int
    metrics: Metrics | None
    trend: str


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ConversationIn(BaseModel):
    """대화 저장 요청. title을 비우면 첫 메시지 앞부분이 제목이 된다."""
    title: str | None = Field(default=None, max_length=100)
    messages: list[Message] = Field(min_length=1, max_length=200)


class ConversationOverview(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[Message]


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000, examples=["가장 더웠던 달은 언제야?"])
    conversation_id: str | None = Field(default=None, description="이어서 대화할 때만 넣는다. 비우면 새 대화가 저장된다.")


class ChatOut(BaseModel):
    reply: str
    conversation_id: str
