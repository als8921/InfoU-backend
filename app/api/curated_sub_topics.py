from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from app.database.database import get_db
from app.models import CuratedSubTopic, Level, MainTopic
from app.schemas.curated_sub_topic import CuratedSubTopicResponse, CuratedSubTopicWithRelations, PaginatedResponse

router = APIRouter(
    prefix="/sub-topics/curated",
    tags=["Curated Sub Topics"]
)


@router.get("", response_model=PaginatedResponse)
async def get_curated_sub_topics(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    level_id: Optional[int] = Query(None, description="난이도 ID로 필터링"),
    main_topic_id: Optional[int] = Query(None, description="대주제 ID로 필터링"),
    is_active: Optional[bool] = Query(True, description="활성 상태로 필터링"),
    search: Optional[str] = Query(None, description="제목 검색"),
    order_by: Optional[str] = Query("title", description="정렬 기준: title, created_at, popularity_score, difficulty_score")
) -> PaginatedResponse:
    """
    큐레이션 소주제 목록 조회 (페이징)
    """
    query = db.query(CuratedSubTopic).options(
        joinedload(CuratedSubTopic.level),
        joinedload(CuratedSubTopic.main_topic)
    )
    
    # 필터링
    if level_id is not None:
        query = query.filter(CuratedSubTopic.level_id == level_id)
    if main_topic_id is not None:
        query = query.filter(CuratedSubTopic.main_topic_id == main_topic_id)
    if is_active is not None:
        query = query.filter(CuratedSubTopic.is_active == is_active)
    if search:
        query = query.filter(CuratedSubTopic.title.contains(search))
    
    # 정렬
    if order_by == "created_at":
        query = query.order_by(desc(CuratedSubTopic.created_at))
    elif order_by == "popularity_score":
        query = query.order_by(desc(CuratedSubTopic.popularity_score))
    elif order_by == "difficulty_score":
        query = query.order_by(CuratedSubTopic.difficulty_score)
    else:  # default: title
        query = query.order_by(CuratedSubTopic.title)
    
    # 전체 개수 계산
    total = query.count()
    
    # 페이징 적용
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 응답 데이터 구성
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[CuratedSubTopicWithRelations.model_validate(item).model_dump() for item in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.get("/by-level/{level_code}", response_model=List[CuratedSubTopicWithRelations])
async def get_curated_sub_topics_by_level(
    level_code: str,
    db: Session = Depends(get_db),
    is_active: bool = Query(True, description="활성 상태로 필터링"),
    limit: int = Query(50, ge=1, le=100, description="최대 개수")
) -> List[CuratedSubTopicWithRelations]:
    """
    특정 난이도의 큐레이션 소주제 목록 조회
    """
    # 난이도 조회
    level = db.query(Level).filter(Level.code == level_code).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # 해당 난이도의 소주제 조회
    sub_topics = db.query(CuratedSubTopic).options(
        joinedload(CuratedSubTopic.level),
        joinedload(CuratedSubTopic.main_topic)
    ).filter(
        CuratedSubTopic.level_id == level.id,
        CuratedSubTopic.is_active == is_active
    ).order_by(desc(CuratedSubTopic.popularity_score), CuratedSubTopic.title).limit(limit).all()
    
    return sub_topics


@router.get("/by-main-topic/{topic_id}", response_model=List[CuratedSubTopicWithRelations])
async def get_curated_sub_topics_by_main_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    is_active: bool = Query(True, description="활성 상태로 필터링"),
    order_by: str = Query("difficulty_score", description="정렬 기준")
) -> List[CuratedSubTopicWithRelations]:
    """
    특정 대주제의 큐레이션 소주제 목록 조회
    """
    # 대주제 존재 확인
    main_topic = db.query(MainTopic).filter(MainTopic.id == topic_id).first()
    if not main_topic:
        raise HTTPException(status_code=404, detail="Main topic not found")
    
    query = db.query(CuratedSubTopic).options(
        joinedload(CuratedSubTopic.level),
        joinedload(CuratedSubTopic.main_topic)
    ).filter(
        CuratedSubTopic.main_topic_id == topic_id,
        CuratedSubTopic.is_active == is_active
    )
    
    # 정렬
    if order_by == "difficulty_score":
        query = query.order_by(CuratedSubTopic.difficulty_score)
    elif order_by == "popularity_score":
        query = query.order_by(desc(CuratedSubTopic.popularity_score))
    elif order_by == "created_at":
        query = query.order_by(desc(CuratedSubTopic.created_at))
    else:
        query = query.order_by(CuratedSubTopic.title)
    
    sub_topics = query.all()
    
    return sub_topics


@router.get("/{sub_topic_id}", response_model=CuratedSubTopicWithRelations)
async def get_curated_sub_topic(
    sub_topic_id: int,
    db: Session = Depends(get_db)
) -> CuratedSubTopicWithRelations:
    """
    특정 큐레이션 소주제 상세 조회
    """
    sub_topic = db.query(CuratedSubTopic).options(
        joinedload(CuratedSubTopic.level),
        joinedload(CuratedSubTopic.main_topic)
    ).filter(CuratedSubTopic.id == sub_topic_id).first()
    
    if not sub_topic:
        raise HTTPException(status_code=404, detail="Curated sub topic not found")
    
    return sub_topic


@router.get("/popular/{level_code}", response_model=List[CuratedSubTopicWithRelations])
async def get_popular_curated_sub_topics(
    level_code: str,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="인기 소주제 개수")
) -> List[CuratedSubTopicWithRelations]:
    """
    특정 난이도의 인기 큐레이션 소주제 목록 조회
    """
    # 난이도 조회
    level = db.query(Level).filter(Level.code == level_code).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # 인기 소주제 조회 (인기도 점수 기준 내림차순)
    sub_topics = db.query(CuratedSubTopic).options(
        joinedload(CuratedSubTopic.level),
        joinedload(CuratedSubTopic.main_topic)
    ).filter(
        CuratedSubTopic.level_id == level.id,
        CuratedSubTopic.is_active == True,
        CuratedSubTopic.popularity_score > 0
    ).order_by(desc(CuratedSubTopic.popularity_score)).limit(limit).all()
    
    return sub_topics