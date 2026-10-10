"""
AI 채팅 (컨텍스트 주입)

흐름: 데이터 요약 조회 → 시스템 프롬프트에 삽입 → AI 호출 → 대화 자동 저장
AI는 Google Gemini를 OpenAI 호환 주소로 호출한다. (openai 패키지를 그대로 사용)
"""
import os
from functools import lru_cache

from openai import OpenAI

from services import conversations, data

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_MODEL = "gemini-3.5-flash"
MAX_TOKENS = 1000      # 비용 제한: 답변 길이 상한
HISTORY_LIMIT = 10     # 비용 제한: 이전 대화는 최근 10개 메시지만 전달
TIMEOUT_SECONDS = 30   # AI가 응답하지 않으면 오래 기다리지 않고 오류로 알린다

SYSTEM_PROMPT = """당신은 서울 기온 데이터 분석 비서입니다.

[사용자 데이터 요약]
- 데이터: 서울 월평균 기온(℃), 한 달에 1개
- 데이터 기간: {period}
- 총 레코드: {count}개
- 주요 지표: 평균 {average}℃, 최고 {max}℃ ({max_date}), 최저 {min}℃ ({min_date})
- 최근 트렌드: {trend}

위 데이터를 기반으로 한국어로 간결하게 맞춤형 답변을 제공하세요.
요약에 없는 수치는 지어내지 말고, 모르면 모른다고 답하세요."""

NO_DATA_PROMPT = "당신은 데이터 분석 비서입니다. 아직 저장된 데이터가 없으니, 데이터를 먼저 추가해 달라고 안내하세요."


class ChatConfigError(RuntimeError):
    """AI 키가 설정되지 않았을 때"""


@lru_cache
def _client() -> OpenAI:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ChatConfigError("GEMINI_API_KEY 가 설정되지 않았습니다.")
    return OpenAI(api_key=api_key, base_url=os.getenv("LLM_BASE_URL", GEMINI_BASE_URL),
                  timeout=TIMEOUT_SECONDS, max_retries=2)


def build_system_prompt(summary: dict) -> str:
    if not summary["count"]:
        return NO_DATA_PROMPT
    return SYSTEM_PROMPT.format(period=summary["period"], count=summary["count"],
                                trend=summary["trend"], **summary["metrics"])


def chat(message: str, conversation_id: str | None = None) -> dict | None:
    """답변과 저장된 대화 id를 돌려준다. conversation_id가 없는 대화면 None."""
    history = []
    if conversation_id:
        conversation = conversations.get_conversation(conversation_id)
        if conversation is None:
            return None
        history = conversation["messages"][-HISTORY_LIMIT:]

    user_message = {"role": "user", "content": message}
    response = _client().chat.completions.create(
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        messages=[{"role": "system", "content": build_system_prompt(data.get_summary())}, *history, user_message],
        max_tokens=MAX_TOKENS,
        reasoning_effort="none",   # 생각 단계를 끄면 답이 빨라지고, 답변이 중간에 잘리지 않는다
    )
    reply = response.choices[0].message.content or "답변을 만들지 못했어요. 질문을 조금 바꿔서 다시 시도해 주세요."

    new_messages = [user_message, {"role": "assistant", "content": reply}]
    if conversation_id:
        conversations.append_messages(conversation_id, new_messages)
    else:
        conversation_id = conversations.create_conversation(new_messages)["id"]
    return {"reply": reply, "conversation_id": conversation_id}
