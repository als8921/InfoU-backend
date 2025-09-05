from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import LearningPath, CurriculumItem, Article
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["CurriculumItem"])

# Response Models
class CurriculumItemResponse(BaseModel):
    curriculum_item_id: str
    title: str
    sort_order: int
    has_articles: bool


@router.get("/learning-paths/{path_id}/curriculum-items", response_model=List[CurriculumItemResponse])
async def get_curriculum_items(path_id: str, db: Session = Depends(get_db)):
    """커리큘럼 아이템 목록 조회"""
    # 학습 경로 존재 확인
    learning_path = db.query(LearningPath).filter(LearningPath.path_id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # 커리큘럼 아이템들 조회 (순서대로)
    curriculum_items = db.query(CurriculumItem).filter(
        CurriculumItem.path_id == path_id
    ).order_by(CurriculumItem.sort_order).all()
    
    result = []
    for item in curriculum_items:
        # 각 커리큘럼 아이템에 글이 있는지 확인
        has_articles = db.query(Article).filter(
            Article.curriculum_item_id == item.curriculum_item_id
        ).count() > 0
        
        result.append(CurriculumItemResponse(
            curriculum_item_id=item.curriculum_item_id,
            title=item.title,
            sort_order=item.sort_order,
            has_articles=has_articles
        ))
    
    return result