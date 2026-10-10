"""데이터 API (CRUD 4개 + 요약 1개)"""
from fastapi import APIRouter, HTTPException, status

from schemas import DataIn, DataOut, Summary
from services import data as data_service

router = APIRouter(prefix="/api/data", tags=["데이터"])

NOT_FOUND = "해당 id의 데이터를 찾을 수 없습니다."


@router.post("", response_model=DataOut, status_code=status.HTTP_201_CREATED, summary="새 데이터 추가")
def create_data(item: DataIn):
    return data_service.create_data(item)


@router.get("", response_model=list[DataOut], summary="데이터 목록 조회 (날짜순)")
def list_data():
    return data_service.list_data()


# /{data_id} 보다 먼저 등록해야 'summary'가 id로 해석되지 않는다.
@router.get("/summary", response_model=Summary, summary="데이터 요약 (프롬프트 주입용)")
def get_summary():
    return data_service.get_summary()


@router.put("/{data_id}", response_model=DataOut, summary="데이터 수정")
def update_data(data_id: str, item: DataIn):
    updated = data_service.update_data(data_id, item)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return updated


@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT, summary="데이터 삭제")
def delete_data(data_id: str):
    if not data_service.delete_data(data_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
