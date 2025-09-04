from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class MainTopicBase(BaseModel):
    """MainTopic 기본 스키마"""
    name: str
    description: Optional[str] = None


class MainTopicCreate(MainTopicBase):
    """MainTopic 생성 스키마"""
    pass


class MainTopicUpdate(BaseModel):
    """MainTopic 업데이트 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None


class MainTopicResponse(MainTopicBase):
    """MainTopic 응답 스키마"""
    main_topic_id: int
    
    model_config = ConfigDict(from_attributes=True)


class MainTopicWithStats(MainTopicResponse):
    """MainTopic 통계 포함 응답 스키마"""
    curated_sub_topics_count: int = 0