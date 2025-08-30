from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class LevelBase(BaseModel):
    """Level 기본 스키마"""
    code: str
    name: str
    description: str
    target_audience: str
    characteristics: List[str]
    estimated_hours_per_week: int
    order: int


class LevelCreate(LevelBase):
    """Level 생성 스키마"""
    pass


class LevelUpdate(BaseModel):
    """Level 업데이트 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    characteristics: Optional[List[str]] = None
    estimated_hours_per_week: Optional[int] = None


class LevelResponse(LevelBase):
    """Level 응답 스키마"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class LevelWithStats(LevelResponse):
    """Level 통계 포함 응답 스키마"""
    main_topics_count: int = 0
    curated_sub_topics_count: int = 0