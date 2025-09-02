from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class GeneratedSubTopicBase(BaseModel):
    """생성된 소주제 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=300, description="소주제 제목")
    description: Optional[str] = Field(None, description="소주제 설명")
    keywords: Optional[List[str]] = Field(default=[], description="관련 키워드")
    learning_objectives: Optional[List[str]] = Field(default=[], description="학습 목표")
    prerequisites: Optional[List[str]] = Field(default=[], description="선행 지식")
    estimated_duration_minutes: Optional[int] = Field(None, ge=1, le=600, description="예상 학습 시간(분)")
    difficulty_score: Optional[int] = Field(None, ge=1, le=10, description="난이도 점수 (1-10)")


class GeneratedSubTopicCreate(GeneratedSubTopicBase):
    """소주제 생성 요청 스키마"""
    main_topic_id: int = Field(..., description="대주제 ID")
    generation_request_id: int = Field(..., description="생성 요청 ID")
    quality_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="품질 점수")


class GeneratedSubTopicResponse(GeneratedSubTopicBase):
    """소주제 응답 스키마"""
    id: int
    main_topic_id: int
    generation_request_id: int
    is_active: bool
    quality_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubTopicGenerationRequestCreate(BaseModel):
    """소주제 생성 요청 생성 스키마"""
    main_topic_id: int = Field(..., description="대주제 ID")
    personalization_data: Optional[Dict[str, Any]] = Field(default={}, description="개인화 정보")
    generation_parameters: Optional[Dict[str, Any]] = Field(
        default={"count": 10, "difficulty_preference": "medium"}, 
        description="생성 파라미터"
    )


class SubTopicGenerationRequestResponse(BaseModel):
    """소주제 생성 요청 응답 스키마"""
    id: int
    user_id: int
    main_topic_id: int
    personalization_data: Optional[Dict[str, Any]]
    generation_parameters: Optional[Dict[str, Any]]
    status: str
    tokens_used: int
    cost_usd: float
    model_used: Optional[str]
    total_generated: int
    quality_score: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    # 생성된 소주제들
    generated_sub_topics: List[GeneratedSubTopicResponse] = []

    class Config:
        from_attributes = True


class PersonalizationData(BaseModel):
    """개인화 데이터 스키마"""
    learning_level: Optional[str] = Field(None, description="학습 수준: beginner, intermediate, advanced")
    learning_goals: Optional[List[str]] = Field(default=[], description="학습 목표")
    preferred_difficulty: Optional[str] = Field(None, description="선호 난이도: easy, medium, hard")
    time_preference: Optional[int] = Field(None, ge=10, le=180, description="선호 학습 시간(분)")
    learning_style: Optional[str] = Field(None, description="학습 스타일: visual, auditory, kinesthetic")


class GenerationParameters(BaseModel):
    """생성 파라미터 스키마"""
    count: int = Field(10, ge=1, le=20, description="생성할 소주제 수")
    difficulty_preference: str = Field("medium", description="난이도 선호도: easy, medium, hard, mixed")
    focus_areas: Optional[List[str]] = Field(default=[], description="집중할 영역들")
    exclude_topics: Optional[List[str]] = Field(default=[], description="제외할 주제들")


class SubTopicGenerationResult(BaseModel):
    """소주제 생성 결과 스키마"""
    generation_request_id: int
    status: str
    sub_topics: List[GeneratedSubTopicResponse]
    total_generated: int
    tokens_used: int
    cost_usd: float
    quality_score: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]