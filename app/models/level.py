from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base


class Level(Base):
    """난이도 모델 (5단계)"""
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # absolute_beginner, beginner, etc.
    name = Column(String(100), nullable=False)  # 완전 초심자, 초심자, etc.
    description = Column(Text, nullable=False)
    target_audience = Column(String(200), nullable=False)
    characteristics = Column(JSON, nullable=False)  # 특징들을 JSON 배열로 저장
    estimated_hours_per_week = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False, index=True)

    # 관계 설정
    curated_sub_topics = relationship("CuratedSubTopic", back_populates="level", cascade="all, delete-orphan")

    class Config:
        orm_mode = True