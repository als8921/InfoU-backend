from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import SubTopic, LearningPath, CurriculumItem
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["LearningPath"])

# Response Models
class CurriculumItemResponse(BaseModel):
    curriculum_item_id: str
    title: str
    sort_order: int

class LearningPathListResponse(BaseModel):
    path_id: str
    title: str
    description: str
    curriculum_count: int
    estimated_hours: int

class LearningPathDetailResponse(BaseModel):
    path_id: str
    title: str
    description: str
    curriculum_items: List[CurriculumItemResponse]

class GenerateLearningPathRequest(BaseModel):
    learning_objective: str
    difficulty: str
    item_count: int

class GenerateLearningPathResponse(BaseModel):
    path_id: str
    title: str
    curriculum_items: List[CurriculumItemResponse]


@router.get("/sub-topics/{sub_topic_id}/learning-paths", response_model=List[LearningPathListResponse])
async def get_learning_paths(sub_topic_id: int, db: Session = Depends(get_db)):
    """학습 경로 목록 조회"""
    # 소주제 존재 확인
    sub_topic = db.query(SubTopic).filter(SubTopic.sub_topic_id == sub_topic_id).first()
    if not sub_topic:
        raise HTTPException(status_code=404, detail="Sub topic not found")
    
    # 학습 경로들 조회
    learning_paths = db.query(LearningPath).filter(
        LearningPath.sub_topic_id == sub_topic_id
    ).all()
    
    result = []
    for path in learning_paths:
        # 각 경로의 커리큘럼 수 계산
        curriculum_count = db.query(CurriculumItem).filter(
            CurriculumItem.path_id == path.path_id
        ).count()
        
        result.append(LearningPathListResponse(
            path_id=path.path_id,
            title=path.title,
            description=path.description or "",
            curriculum_count=curriculum_count,
            estimated_hours=curriculum_count * 2  # 더미 계산: 커리큘럼당 2시간
        ))
    
    return result


@router.get("/learning-paths/{path_id}", response_model=LearningPathDetailResponse)
async def get_learning_path_detail(path_id: str, db: Session = Depends(get_db)):
    """특정 학습 경로 상세 조회"""
    # 학습 경로 존재 확인
    learning_path = db.query(LearningPath).filter(LearningPath.path_id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # 커리큘럼 아이템들 조회 (순서대로)
    curriculum_items = db.query(CurriculumItem).filter(
        CurriculumItem.path_id == path_id
    ).order_by(CurriculumItem.sort_order).all()
    
    return LearningPathDetailResponse(
        path_id=learning_path.path_id,
        title=learning_path.title,
        description=learning_path.description or "",
        curriculum_items=[
            CurriculumItemResponse(
                curriculum_item_id=item.curriculum_item_id,
                title=item.title,
                sort_order=item.sort_order
            )
            for item in curriculum_items
        ]
    )


@router.post("/sub-topics/{sub_topic_id}/learning-paths/generate", response_model=GenerateLearningPathResponse)
async def generate_learning_path(
    sub_topic_id: int,
    request: GenerateLearningPathRequest,
    db: Session = Depends(get_db)
):
    """AI 커리큘럼 생성"""
    # 소주제 존재 확인
    sub_topic = db.query(SubTopic).filter(SubTopic.sub_topic_id == sub_topic_id).first()
    if not sub_topic:
        raise HTTPException(status_code=404, detail="Sub topic not found")
    
    # TODO: 실제 AI 생성 로직 구현 필요
    # 더미 학습 경로 생성
    import uuid
    path_id = f"path_{uuid.uuid4().hex[:8]}"
    
    new_path = LearningPath(
        path_id=path_id,
        sub_topic_id=sub_topic_id,
        title=f"{request.learning_objective} - {request.difficulty} 과정",
        description=f"{request.learning_objective}를 위한 {request.difficulty} 수준의 학습 과정",
        is_default=False
    )
    
    db.add(new_path)
    db.flush()  # path_id를 얻기 위해
    
    # 더미 커리큘럼 아이템들 생성
    curriculum_items = []
    for i in range(request.item_count):
        item_id = f"item_{uuid.uuid4().hex[:8]}"
        curriculum_item = CurriculumItem(
            curriculum_item_id=item_id,
            sub_topic_id=sub_topic_id,
            path_id=path_id,
            title=f"{request.learning_objective} - {i+1}단계",
            sort_order=i+1
        )
        db.add(curriculum_item)
        curriculum_items.append(CurriculumItemResponse(
            curriculum_item_id=item_id,
            title=curriculum_item.title,
            sort_order=curriculum_item.sort_order
        ))
    
    db.commit()
    
    return GenerateLearningPathResponse(
        path_id=path_id,
        title=new_path.title,
        curriculum_items=curriculum_items
    )