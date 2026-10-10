# 서울 기온 AI 비서

내 데이터를 아는 AI 비서입니다. 서울의 월평균 기온 100개월치를 Firestore에 저장하고, 그 요약을 AI에게 알려준 뒤 대화합니다. "가장 더웠던 달은 언제야?"처럼 물으면 일반적인 답이 아니라 저장된 데이터에 근거한 답을 받습니다.

## 배포 주소

| | 주소 |
|---|---|
| 프론트엔드 (Vercel) | https://ai-assistant-frontend-mauve.vercel.app |
| 백엔드 API (Render) | https://ai-assistant-api-qc8n.onrender.com |
| Swagger UI | https://ai-assistant-api-qc8n.onrender.com/docs |

백엔드는 Render 무료 서버라 한동안 쓰지 않으면 잠듭니다. 첫 요청은 최대 1분쯤 걸릴 수 있고, 이때 화면에 "서버를 깨우는 중" 안내가 표시됩니다.

## 주요 기능

1. **데이터 기반 AI 채팅**: 질문하면 데이터 요약을 반영한 답변을 받습니다. 답변을 기다리는 동안 로딩이 표시되고, 대화는 자동 저장됩니다.
2. **데이터 관리**: (날짜, 기온, 메모) 데이터를 추가·수정·삭제합니다. 바꾸면 요약도 바로 갱신됩니다.
3. **대화 기록**: 이전 대화 목록을 보고, 골라서 다시 불러오거나 삭제합니다.
4. **데이터 요약**: 기간, 개수, 평균, 최고, 최저, 최근 추세를 항상 화면 위에 보여줍니다.

## 기술 스택

| 영역 | 사용 기술 |
|---|---|
| 백엔드 | Python, FastAPI, Pydantic, Uvicorn |
| 데이터베이스 | Firebase Firestore (`data`, `conversations` 컬렉션) |
| AI | Google Gemini (`gemini-3.5-flash`), `openai` 패키지로 OpenAI 호환 주소 호출 |
| 프론트엔드 | HTML, CSS, JavaScript (프레임워크 없음) |
| 배포 | Render (백엔드), Vercel (프론트엔드) |

AI는 Gemini를 사용합니다. `openai` 패키지의 호출 주소만 Gemini로 지정했기 때문에, `.env`의 `LLM_BASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL` 값을 바꾸면 다른 OpenAI 호환 모델로 교체할 수 있습니다.

## 컨텍스트 주입 방식

AI는 내 데이터를 모릅니다. 그래서 질문을 보낼 때마다 데이터 요약을 시스템 프롬프트에 넣어 함께 보냅니다.

1. `POST /api/chat`으로 질문이 들어옵니다.
2. Firestore의 `data` 컬렉션을 읽어 요약(기간, 개수, 평균/최대/최소, 추세)을 계산합니다.
3. 요약을 시스템 프롬프트의 빈칸에 채웁니다.
4. 시스템 프롬프트, 이전 대화(최근 10개 메시지), 새 질문을 AI에 보냅니다.
5. 질문과 답변을 `conversations` 컬렉션에 저장합니다.

데이터를 수정하면 다음 질문부터 바뀐 요약이 반영됩니다.

## API

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/data` | 새 데이터 추가 |
| GET | `/api/data` | 데이터 목록 (날짜순) |
| PUT | `/api/data/{id}` | 데이터 수정 |
| DELETE | `/api/data/{id}` | 데이터 삭제 |
| GET | `/api/data/summary` | 데이터 요약 (프롬프트 주입용) |
| POST | `/api/conversations` | 대화 저장 |
| GET | `/api/conversations` | 대화 목록 (최근순, 본문 제외) |
| GET | `/api/conversations/{id}` | 대화 불러오기 (전체 메시지) |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| POST | `/api/chat` | AI 채팅 (대화 자동 저장) |

대화 목록은 본문 없이 제목과 메시지 개수만 주고, 본문은 `GET /api/conversations/{id}`로 받습니다.

## 폴더 구조

```
ai-assistant/
├── backend/
│   ├── main.py            # FastAPI 앱, CORS, 라우터 등록
│   ├── schemas.py         # Pydantic 요청/응답 검증
│   ├── routers/           # 주소(엔드포인트) 정의: data, conversations, chat
│   ├── services/          # 실제 처리: firestore, data, summary, conversations, chat
│   ├── scripts/           # 데이터 준비(prepare_data), DB 적재(seed_data)
│   └── data/              # 원본 CSV와 100개월 JSON
└── frontend/              # index.html, style.css, app.js, config.js, build.js
```

라우터는 주소와 입력 검증, 오류 응답만 맡고, 실제 처리는 서비스에 둡니다. 요약 계산(`services/summary.py`)은 DB와 무관한 순수 함수라 스크립트와 API가 같이 씁니다.

## 로컬 실행 방법

Python 3.10 이상이 필요합니다.

```bash
# 1. 백엔드 준비
cd backend
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2. 환경 변수: .env.example 을 .env 로 복사한 뒤 값 채우기
#    Firebase 서비스 계정 키 파일은 backend/serviceAccount.json 으로 저장

# 3. 데이터 100개를 Firestore에 넣기 (처음 한 번)
python -m scripts.seed_data

# 4. 백엔드 실행 → http://127.0.0.1:8000/docs
uvicorn main:app --reload

# 5. 프론트엔드 실행 (새 터미널) → http://localhost:5500
cd ../frontend
python -m http.server 5500
```

## 환경 변수

백엔드 (`backend/.env`, Render 환경 변수)

| 이름 | 설명 |
|---|---|
| `GEMINI_API_KEY` | Gemini API 키 (Google AI Studio에서 발급) |
| `GEMINI_MODEL` | 사용할 모델. 기본값 `gemini-3.5-flash` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | 서비스 계정 키 JSON 내용 전체 (배포용) |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | 서비스 계정 키 파일 경로 (로컬용, 위 값이 없을 때 사용) |
| `ALLOWED_ORIGINS` | CORS 허용 주소 목록 (쉼표로 구분) |

프론트엔드 (Vercel 환경 변수)

| 이름 | 설명 |
|---|---|
| `API_BASE_URL` | 백엔드 주소. 배포 때 `build.js`가 이 값으로 `config.js`를 만듭니다. |

API 키와 서비스 계정 키는 코드에 넣지 않으며, `.env`와 키 파일은 `.gitignore`로 저장소에서 제외합니다.

## 데이터

- 내용: 서울 월평균 기온 100개월 (2017-09 ~ 2025-12). 메모에는 그 달의 폭염일(일최고 33℃ 이상)과 열대야(일최저 25℃ 이상) 일수가 들어 있습니다.
- 만드는 법: 일별 자료 11,323일치를 월별로 평균 (`python -m scripts.prepare_data`)
- 출처: Open-Meteo Historical Weather API, ERA5 재분석 자료 (Copernicus Climate Change Service), CC BY 4.0
- 재분석 자료는 격자 평균값이라 기상청 관측소 공식 통계와 다를 수 있습니다.

## 스크린샷

배포 후 추가: 채팅 화면, 데이터 관리 화면, 대화 기록 화면
