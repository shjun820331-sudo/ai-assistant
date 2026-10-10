"""
데이터 요약 만들기

(date, value, memo) 레코드 목록을 받아 AI 프롬프트에 넣을 요약 정보를 계산한다.
DB와 무관한 순수 계산이라 스크립트와 API 양쪽에서 같이 쓴다.
"""
TREND_WINDOW = 12        # 최근 12개와 그 전 12개를 비교
TREND_FLAT_BELOW = 0.1   # 차이가 이 값(℃) 미만이면 '유지'


def summarize(records: list[dict]) -> dict:
    if not records:
        return {"period": None, "count": 0, "metrics": None, "trend": "데이터 없음"}

    rows = sorted(records, key=lambda r: r["date"])
    values = [r["value"] for r in rows]
    hottest = max(rows, key=lambda r: r["value"])
    coldest = min(rows, key=lambda r: r["value"])

    return {
        "period": f"{rows[0]['date'][:7]} ~ {rows[-1]['date'][:7]}",
        "count": len(rows),
        "metrics": {
            "average": round(sum(values) / len(values), 2),
            "max": hottest["value"],
            "max_date": hottest["date"],
            "min": coldest["value"],
            "min_date": coldest["date"],
        },
        "trend": _trend(values),
    }


def _trend(values: list[float]) -> str:
    if len(values) < TREND_WINDOW * 2:
        return "판단 불가 (데이터 부족)"

    recent = sum(values[-TREND_WINDOW:]) / TREND_WINDOW
    before = sum(values[-TREND_WINDOW * 2:-TREND_WINDOW]) / TREND_WINDOW
    diff = recent - before

    if abs(diff) < TREND_FLAT_BELOW:
        return f"유지 (최근 {TREND_WINDOW}개월 평균 {recent:.2f}℃, 직전 {TREND_WINDOW}개월과 비슷)"
    direction = "상승" if diff > 0 else "하락"
    return f"{direction} (최근 {TREND_WINDOW}개월 평균 {recent:.2f}℃, 직전 {TREND_WINDOW}개월 대비 {diff:+.2f}℃)"
