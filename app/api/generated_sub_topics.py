from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.database.database import get_db
from app.models import User, MainTopic, GeneratedSubTopic, SubTopicGenerationRequest
from app.schemas.generated_sub_topic import (
    SubTopicGenerationRequestCreate,
    SubTopicGenerationRequestResponse,
    GeneratedSubTopicResponse,
    SubTopicGenerationResult
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sub-topics", tags=["generated_sub_topics"])


@router.post("/generate", response_model=SubTopicGenerationRequestResponse)
async def generate_sub_topics(
    request: SubTopicGenerationRequestCreate,
    db: Session = Depends(get_db)
):
    """LLM을 통해 소주제를 생성합니다."""
    
    # 임시로 user_id = 1로 설정 (실제로는 인증에서 가져와야 함)
    user_id = 1
    
    try:
        # 1. 대주제 존재 확인
        main_topic = db.query(MainTopic).filter(MainTopic.id == request.main_topic_id).first()
        if not main_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대주제를 찾을 수 없습니다."
            )
        
        # 2. 생성 요청 레코드 생성
        generation_request = SubTopicGenerationRequest(
            user_id=user_id,
            main_topic_id=request.main_topic_id,
            personalization_data=request.personalization_data,
            generation_parameters=request.generation_parameters,
            status="processing"
        )
        db.add(generation_request)
        db.commit()
        db.refresh(generation_request)
        
        # 3. LLM을 통해 소주제 생성
        count = request.generation_parameters.get("count", 10) if request.generation_parameters else 10
        
        llm_result = await llm_service.generate_sub_topics(
            main_topic_title=main_topic.title,
            main_topic_description=main_topic.description,
            personalization_data=request.personalization_data,
            count=count
        )
        
        # 4. 생성된 소주제들을 DB에 저장
        generated_sub_topics = []
        for sub_topic_data in llm_result["sub_topics"]:
            sub_topic = GeneratedSubTopic(
                title=sub_topic_data["title"],
                description=sub_topic_data.get("description"),
                main_topic_id=request.main_topic_id,
                generation_request_id=generation_request.id,
                keywords=sub_topic_data.get("keywords"),
                learning_objectives=sub_topic_data.get("learning_objectives"),
                prerequisites=sub_topic_data.get("prerequisites"),
                estimated_duration_minutes=sub_topic_data.get("estimated_duration_minutes"),
                difficulty_score=sub_topic_data.get("difficulty_score"),
                quality_score=llm_result.get("quality_score")
            )
            db.add(sub_topic)
            generated_sub_topics.append(sub_topic)
        
        # 5. 생성 요청 완료 처리
        generation_request.status = "completed"
        generation_request.tokens_used = llm_result.get("tokens_used", 0)
        generation_request.cost_usd = calculate_cost(llm_result.get("tokens_used", 0))
        generation_request.model_used = llm_result.get("model_used")
        generation_request.total_generated = len(generated_sub_topics)
        generation_request.quality_score = llm_result.get("quality_score")
        generation_request.completed_at = datetime.utcnow()
        
        db.commit()
        
        # 6. 응답 데이터 준비
        for sub_topic in generated_sub_topics:
            db.refresh(sub_topic)
        
        db.refresh(generation_request)
        
        return generation_request
        
    except Exception as e:
        logger.error(f"소주제 생성 실패: {str(e)}")
        
        # 실패 시 상태 업데이트
        if 'generation_request' in locals():
            generation_request.status = "failed"
            generation_request.error_message = str(e)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"소주제 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/generation-requests/{request_id}", response_model=SubTopicGenerationRequestResponse)
def get_generation_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """생성 요청 결과를 조회합니다."""
    
    generation_request = db.query(SubTopicGenerationRequest).filter(
        SubTopicGenerationRequest.id == request_id
    ).first()
    
    if not generation_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="생성 요청을 찾을 수 없습니다."
        )
    
    return generation_request


@router.get("/generation-requests", response_model=List[SubTopicGenerationRequestResponse])
def list_generation_requests(
    main_topic_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """생성 요청 목록을 조회합니다."""
    
    # 임시로 user_id = 1로 설정
    user_id = 1
    
    query = db.query(SubTopicGenerationRequest).filter(
        SubTopicGenerationRequest.user_id == user_id
    )
    
    if main_topic_id:
        query = query.filter(SubTopicGenerationRequest.main_topic_id == main_topic_id)
    
    if status:
        query = query.filter(SubTopicGenerationRequest.status == status)
    
    generation_requests = query.order_by(
        SubTopicGenerationRequest.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return generation_requests


@router.get("/{sub_topic_id}", response_model=GeneratedSubTopicResponse)
def get_generated_sub_topic(
    sub_topic_id: int,
    db: Session = Depends(get_db)
):
    """생성된 소주제 상세 정보를 조회합니다."""
    
    sub_topic = db.query(GeneratedSubTopic).filter(
        GeneratedSubTopic.id == sub_topic_id,
        GeneratedSubTopic.is_active == True
    ).first()
    
    if not sub_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소주제를 찾을 수 없습니다."
        )
    
    return sub_topic


@router.get("/", response_model=List[GeneratedSubTopicResponse])
def list_generated_sub_topics(
    main_topic_id: int = None,
    generation_request_id: int = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """생성된 소주제 목록을 조회합니다."""
    
    query = db.query(GeneratedSubTopic).filter(
        GeneratedSubTopic.is_active == True
    )
    
    if main_topic_id:
        query = query.filter(GeneratedSubTopic.main_topic_id == main_topic_id)
    
    if generation_request_id:
        query = query.filter(GeneratedSubTopic.generation_request_id == generation_request_id)
    
    sub_topics = query.order_by(
        GeneratedSubTopic.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return sub_topics


@router.delete("/{sub_topic_id}")
def delete_generated_sub_topic(
    sub_topic_id: int,
    db: Session = Depends(get_db)
):
    """생성된 소주제를 삭제합니다 (소프트 삭제)."""
    
    sub_topic = db.query(GeneratedSubTopic).filter(
        GeneratedSubTopic.id == sub_topic_id
    ).first()
    
    if not sub_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소주제를 찾을 수 없습니다."
        )
    
    sub_topic.is_active = False
    db.commit()
    
    return {"message": "소주제가 삭제되었습니다."}


def calculate_cost(tokens_used: int) -> float:
    """토큰 사용량을 기반으로 비용을 계산합니다."""
    # Gemini 1.5 Flash 기준: $0.075 / 1M tokens (input), $0.30 / 1M tokens (output)
    # 간단하게 평균값으로 계산
    cost_per_1m_tokens = 0.1875  # ($0.075 + $0.30) / 2
    return (tokens_used / 1000000) * cost_per_1m_tokens