from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database.database import get_db
from app.models import MainTopic, CuratedSubTopic
from app.schemas.main_topic import MainTopicResponse, MainTopicWithStats
from app.schemas.curated_sub_topic import PaginatedResponse

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
    
    # 필터링
    if is_active is not None:
        query = query.filter(MainTopic.is_active == is_active)
    if search:
        query = query.filter(MainTopic.title.contains(search))
    
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
        MainTopic.id == topic_id
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Main topic not found")
    
    # 큐레이션 소주제 개수 계산
    sub_topics_count = db.query(CuratedSubTopic).filter(
        CuratedSubTopic.main_topic_id == topic.id,
        CuratedSubTopic.is_active == True
    ).count()
    
    topic_dict = {
        "id": topic.id,
        "title": topic.title,
        "description": topic.description,
        "is_active": topic.is_active,
        "created_at": topic.created_at,
        "updated_at": topic.updated_at,
        "curated_sub_topics_count": sub_topics_count
    }
    return MainTopicWithStats(**topic_dict)