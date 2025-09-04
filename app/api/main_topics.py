from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Any, List
from pydantic import BaseModel
from app.database.database import get_db
from app.models import MainTopic, SubTopic
from app.schemas.main_topic import MainTopicResponse, MainTopicWithStats

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

router = APIRouter(
    prefix="/main-topics",
    tags=["Main Topics"]
)


@router.get("", response_model=PaginatedResponse)
async def get_main_topics(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),

    is_active: Optional[bool] = Query(True, description="활성 상태로 필터링"),
    search: Optional[str] = Query(None, description="제목 검색")
) -> PaginatedResponse:
    """
    대주제 목록 조회 (페이징)
    """
    query = db.query(MainTopic)
    
    # 필터링 - 새 스키마에는 is_active가 없으므로 제거
    if search:
        query = query.filter(MainTopic.name.contains(search))
    
    # 전체 개수 계산
    total = query.count()
    
    # 페이징 적용
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 응답 데이터 구성
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[MainTopicResponse.model_validate(item).model_dump() for item in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )





@router.get("/{topic_id}", response_model=MainTopicWithStats)
async def get_main_topic(
    topic_id: int,
    db: Session = Depends(get_db)
) -> MainTopicWithStats:
    """
    특정 대주제 상세 조회
    """
    topic = db.query(MainTopic).filter(
        MainTopic.main_topic_id == topic_id
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Main topic not found")
    
    # 소주제 개수 계산
    sub_topics_count = db.query(SubTopic).filter(
        SubTopic.main_topic_id == topic.main_topic_id
    ).count()
    
    topic_dict = {
        "id": topic.main_topic_id,
        "title": topic.name,
        "description": topic.description,
        "curated_sub_topics_count": sub_topics_count
    }
    return MainTopicWithStats(**topic_dict)