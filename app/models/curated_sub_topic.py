from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class CuratedSubTopic(Base):
    """큐레이션 소주제 모델"""
    __tablename__ = "curated_sub_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    main_topic_id = Column(Integer, ForeignKey("main_topics.id"), nullable=False, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False, index=True)
    
    # 큐레이션 정보
    keywords = Column(JSON, nullable=True)  # 관련 키워드들
    learning_objectives = Column(JSON, nullable=True)  # 학습 목표들
    prerequisites = Column(JSON, nullable=True)  # 선행 지식
    estimated_duration_minutes = Column(Integer, nullable=True)  # 예상 학습 시간 (분)
    
    # 메타데이터
    difficulty_score = Column(Integer, nullable=True)  # 1-10 난이도 점수
    popularity_score = Column(Integer, default=0, nullable=False)  # 인기도 점수
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계 설정
    level = relationship("Level", back_populates="curated_sub_topics")
    main_topic = relationship("MainTopic", back_populates="curated_sub_topics")

    class Config:
        orm_mode = True