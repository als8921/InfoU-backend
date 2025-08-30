from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from app.database.database import get_db
from app.models import MainTopic, Level, CuratedSubTopic
from app.schemas.main_topic import MainTopicResponse, MainTopicWithLevel, MainTopicWithStats
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
    level_id: Optional[int] = Query(None, description="난이도 ID로 필터링"),
    is_active: Optional[bool] = Query(True, description="활성 상태로 필터링"),
    search: Optional[str] = Query(None, description="제목 검색")
) -> PaginatedResponse:
    """
    대주제 목록 조회 (페이징)
    """
    query = db.query(MainTopic).options(joinedload(MainTopic.level))
    
    # 필터링
    if level_id is not None:
        query = query.filter(MainTopic.level_id == level_id)
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
        items=[MainTopicWithLevel.model_validate(item).model_dump() for item in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.get("/by-level/{level_code}", response_model=List[MainTopicWithStats])
async def get_main_topics_by_level(
    level_code: str,
    db: Session = Depends(get_db),
    is_active: bool = Query(True, description="활성 상태로 필터링")
) -> List[MainTopicWithStats]:
    """
    특정 난이도의 대주제 목록 조회 (통계 포함)
    """
    # 난이도 조회
    level = db.query(Level).filter(Level.code == level_code).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # 해당 난이도의 대주제 조회
    main_topics = db.query(MainTopic).options(joinedload(MainTopic.level)).filter(
        MainTopic.level_id == level.id,
        MainTopic.is_active == is_active
    ).order_by(MainTopic.title).all()
    
    result = []
    for topic in main_topics:
        # 큐레이션 소주제 개수 계산
        sub_topics_count = db.query(CuratedSubTopic).filter(
            CuratedSubTopic.main_topic_id == topic.id,
            CuratedSubTopic.is_active == True
        ).count()
        
        topic_dict = {
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "level_id": topic.level_id,
            "is_active": topic.is_active,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
            "curated_sub_topics_count": sub_topics_count,
            "level": topic.level
        }
        topic_with_stats = MainTopicWithStats(**topic_dict)
        result.append(topic_with_stats)
    
    return result


@router.get("/{topic_id}", response_model=MainTopicWithStats)
async def get_main_topic(
    topic_id: int,
    db: Session = Depends(get_db)
) -> MainTopicWithStats:
    """
    특정 대주제 상세 조회
    """
    topic = db.query(MainTopic).options(joinedload(MainTopic.level)).filter(
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
        "level_id": topic.level_id,
        "is_active": topic.is_active,
        "created_at": topic.created_at,
        "updated_at": topic.updated_at,
        "curated_sub_topics_count": sub_topics_count,
        "level": topic.level
    }
    return MainTopicWithStats(**topic_dict)