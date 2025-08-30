from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import Level, MainTopic, CuratedSubTopic
from app.schemas.level import LevelResponse, LevelWithStats

router = APIRouter(
    prefix="/levels",
    tags=["Levels"]
)


@router.get("", response_model=List[LevelResponse])
async def get_levels(db: Session = Depends(get_db)) -> List[LevelResponse]:
    """
    난이도 메타데이터 조회
    5단계 난이도 정보를 반환
    """
    levels = db.query(Level).order_by(Level.order).all()
    return levels


@router.get("/with-stats", response_model=List[LevelWithStats])
async def get_levels_with_stats(db: Session = Depends(get_db)) -> List[LevelWithStats]:
    """
    난이도 메타데이터 조회 (통계 포함)
    각 난이도별 대주제, 소주제 개수 포함
    """
    levels = db.query(Level).order_by(Level.order).all()
    result = []
    
    for level in levels:
        main_topics_count = db.query(MainTopic).filter(
            MainTopic.level_id == level.id,
            MainTopic.is_active == True
        ).count()
        
        curated_sub_topics_count = db.query(CuratedSubTopic).filter(
            CuratedSubTopic.level_id == level.id,
            CuratedSubTopic.is_active == True
        ).count()
        
        level_with_stats = LevelWithStats(
            **level.__dict__,
            main_topics_count=main_topics_count,
            curated_sub_topics_count=curated_sub_topics_count
        )
        result.append(level_with_stats)
    
    return result


@router.get("/{level_code}", response_model=LevelResponse)
async def get_level_by_code(level_code: str, db: Session = Depends(get_db)) -> LevelResponse:
    """
    특정 난이도 코드로 상세 정보 조회
    """
    level = db.query(Level).filter(Level.code == level_code).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    return level