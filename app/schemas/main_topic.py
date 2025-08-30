from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class MainTopicBase(BaseModel):
    """MainTopic 기본 스키마"""
    title: str
    description: Optional[str] = None
    is_active: bool = True


class MainTopicCreate(MainTopicBase):
    """MainTopic 생성 스키마"""
    pass


class MainTopicUpdate(BaseModel):
    """MainTopic 업데이트 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MainTopicResponse(MainTopicBase):
    """MainTopic 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MainTopicWithStats(MainTopicResponse):
    """MainTopic 통계 포함 응답 스키마"""
    curated_sub_topics_count: int = 0