from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import SubTopic, LearningPath, CurriculumItem
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["MVP Learning Paths"])

# Response Models
class CurriculumItemResponse(BaseModel):
    curriculum_item_id: str
    title: str
    sort_order: int

class LearningPathResponse(BaseModel):
    path_id: str
    title: str
    curriculum_items: List[CurriculumItemResponse]


@router.get("/sub-topics/{sub_topic_id}/learning-path", response_model=LearningPathResponse)
async def get_learning_path(sub_topic_id: int, db: Session = Depends(get_db)):
    """기본 학습 경로 조회"""
    # 소주제 존재 확인
    sub_topic = db.query(SubTopic).filter(SubTopic.sub_topic_id == sub_topic_id).first()
    if not sub_topic:
        raise HTTPException(status_code=404, detail="Sub topic not found")
    
    # 기본 학습 경로 조회 (is_default=True 또는 첫 번째 경로)
    learning_path = db.query(LearningPath).filter(
        LearningPath.sub_topic_id == sub_topic_id,
        LearningPath.is_default == True
    ).first()
    
    if not learning_path:
        # 기본 경로가 없으면 첫 번째 경로 사용
        learning_path = db.query(LearningPath).filter(
            LearningPath.sub_topic_id == sub_topic_id
        ).first()
    
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # 커리큘럼 아이템들 조회 (순서대로)
    curriculum_items = db.query(CurriculumItem).filter(
        CurriculumItem.path_id == learning_path.path_id
    ).order_by(CurriculumItem.sort_order).all()
    
    return LearningPathResponse(
        path_id=learning_path.path_id,
        title=learning_path.title,
        curriculum_items=[
            CurriculumItemResponse(
                curriculum_item_id=item.curriculum_item_id,
                title=item.title,
                sort_order=item.sort_order
            )
            for item in curriculum_items
        ]
    )