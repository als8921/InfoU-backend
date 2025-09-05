from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import MainTopic, SubTopic
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["MainTopic & SubTopic"])

# Response Models
class MainTopicResponse(BaseModel):
    main_topic_id: int
    name: str
    description: str

class SubTopicResponse(BaseModel):
    sub_topic_id: int
    name: str
    description: str
    source_type: str

class GenerateSubTopicRequest(BaseModel):
    topic_hint: str

class GenerateSubTopicResponse(BaseModel):
    sub_topic_id: int
    name: str
    description: str
    source_type: str = "generated"


# MainTopic APIs
@router.get("/main-topics", response_model=List[MainTopicResponse])
async def get_main_topics(db: Session = Depends(get_db)):
    """대주제 목록 조회"""
    topics = db.query(MainTopic).all()
    return [
        MainTopicResponse(
            main_topic_id=topic.main_topic_id,
            name=topic.name,
            description=topic.description or ""
        )
        for topic in topics
    ]


# SubTopic APIs
@router.get("/main-topics/{main_topic_id}/sub-topics", response_model=List[SubTopicResponse])
async def get_sub_topics(main_topic_id: int, db: Session = Depends(get_db)):
    """소주제 목록 조회"""
    # 대주제 존재 확인
    main_topic = db.query(MainTopic).filter(MainTopic.main_topic_id == main_topic_id).first()
    if not main_topic:
        raise HTTPException(status_code=404, detail="Main topic not found")
    
    # 소주제 조회
    sub_topics = db.query(SubTopic).filter(SubTopic.main_topic_id == main_topic_id).all()
    
    return [
        SubTopicResponse(
            sub_topic_id=sub_topic.sub_topic_id,
            name=sub_topic.name,
            description=sub_topic.description or "",
            source_type=sub_topic.source_type
        )
        for sub_topic in sub_topics
    ]


@router.post("/main-topics/{main_topic_id}/sub-topics/generate", response_model=GenerateSubTopicResponse)
async def generate_sub_topic(
    main_topic_id: int, 
    request: GenerateSubTopicRequest,
    db: Session = Depends(get_db)
):
    """AI 소주제 생성"""
    # 대주제 존재 확인
    main_topic = db.query(MainTopic).filter(MainTopic.main_topic_id == main_topic_id).first()
    if not main_topic:
        raise HTTPException(status_code=404, detail="Main topic not found")
    
    # TODO: 실제 AI 생성 로직 구현 필요
    # 현재는 더미 데이터 생성
    new_sub_topic = SubTopic(
        main_topic_id=main_topic_id,
        name=f"{request.topic_hint} 입문",
        description=f"{request.topic_hint}에 대한 기초 학습 내용",
        source_type="generated"
    )
    
    db.add(new_sub_topic)
    db.commit()
    db.refresh(new_sub_topic)
    
    return GenerateSubTopicResponse(
        sub_topic_id=new_sub_topic.sub_topic_id,
        name=new_sub_topic.name,
        description=new_sub_topic.description,
        source_type=new_sub_topic.source_type
    )