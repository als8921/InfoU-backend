from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class LevelBase(BaseModel):
    """Level 기본 스키마"""
    level_code: str
    name: str
    description: Optional[str] = None


class LevelCreate(LevelBase):
    """Level 생성 스키마"""
    pass


class LevelUpdate(BaseModel):
    """Level 업데이트 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None


class LevelResponse(LevelBase):
    """Level 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)


class LevelWithStats(LevelResponse):
    """Level 통계 포함 응답 스키마"""
    main_topics_count: int = 0
    curated_sub_topics_count: int = 0