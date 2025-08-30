from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Generic, TypeVar, Any
from datetime import datetime
from .level import LevelResponse
from .main_topic import MainTopicResponse

T = TypeVar('T')


class CuratedSubTopicBase(BaseModel):
    """CuratedSubTopic 기본 스키마"""
    title: str
    description: Optional[str] = None
    main_topic_id: int
    level_id: int
    keywords: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    estimated_duration_minutes: Optional[int] = None
    difficulty_score: Optional[int] = None
    popularity_score: int = 0
    is_active: bool = True


class CuratedSubTopicCreate(CuratedSubTopicBase):
    """CuratedSubTopic 생성 스키마"""
    pass


class CuratedSubTopicUpdate(BaseModel):
    """CuratedSubTopic 업데이트 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    main_topic_id: Optional[int] = None
    level_id: Optional[int] = None
    keywords: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    estimated_duration_minutes: Optional[int] = None
    difficulty_score: Optional[int] = None
    popularity_score: Optional[int] = None
    is_active: Optional[bool] = None


class CuratedSubTopicResponse(CuratedSubTopicBase):
    """CuratedSubTopic 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CuratedSubTopicWithRelations(CuratedSubTopicResponse):
    """CuratedSubTopic with relations 응답 스키마"""
    level: LevelResponse
    main_topic: MainTopicResponse


# 페이징 관련 스키마
class PaginationParams(BaseModel):
    """페이징 매개변수"""
    page: int = 1
    size: int = 20
    
    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.size < 1 or self.size > 100:
            self.size = 20


class PaginatedResponse(BaseModel):
    """페이징된 응답 스키마"""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool