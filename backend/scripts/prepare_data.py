"""
일별 기온 CSV → 최근 100개월 월평균 데이터로 변환

실행(backend 폴더에서):  python -m scripts.prepare_data
입력:  data/seoul_weather_1995_2025.csv   (Open-Meteo, 일별 11,323행)
결과:  data/seoul_monthly_100.json        ((date, value, memo) 100개)
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

from services.summary import summarize

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCE = DATA_DIR / "seoul_weather_1995_2025.csv"
OUT = DATA_DIR / "seoul_monthly_100.json"
MONTHS = 100
HEATWAVE_MAX = 33.0   # 폭염일: 일최고 33℃ 이상
TROPICAL_MIN = 25.0   # 열대야: 일최저 25℃ 이상


def main():
    by_month = defaultdict(list)
    with SOURCE.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_month[row["date"][:7]].append(row)

    records = []
    for month in sorted(by_month)[-MONTHS:]:
        days = by_month[month]
        mean = sum(float(d["temp_mean"]) for d in days) / len(days)
        heatwave = sum(float(d["temp_max"]) >= HEATWAVE_MAX for d in days)
        tropical = sum(float(d["temp_min"]) >= TROPICAL_MIN for d in days)
        notes = [f"폭염일 {heatwave}일"] if heatwave else []
        notes += [f"열대야 {tropical}일"] if tropical else []
        records.append({"date": f"{month}-01", "value": round(mean, 2), "memo": ", ".join(notes)})

    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장 완료: {OUT.name} ({len(records)}개)")
    print(json.dumps(summarize(records), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
