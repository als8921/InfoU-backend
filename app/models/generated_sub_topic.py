from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class GeneratedSubTopic(Base):
    """LLM으로 생성된 소주제 모델"""
    __tablename__ = "generated_sub_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    main_topic_id = Column(Integer, ForeignKey("main_topics.id"), nullable=False, index=True)
    generation_request_id = Column(Integer, ForeignKey("subtopic_generation_requests.id"), nullable=False, index=True)
    
    # AI 생성 정보
    keywords = Column(JSON, nullable=True)
    learning_objectives = Column(JSON, nullable=True)
    prerequisites = Column(JSON, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    difficulty_score = Column(Integer, nullable=True)  # 1-10
    
    # 메타데이터
    is_active = Column(Boolean, default=True, nullable=False)
    quality_score = Column(Float, nullable=True)  # AI 품질 평가 점수
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계 설정
    main_topic = relationship("MainTopic")
    generation_request = relationship("SubTopicGenerationRequest", back_populates="generated_sub_topics")

    class Config:
        orm_mode = True


class SubTopicGenerationRequest(Base):
    """소주제 생성 요청 추적 모델"""
    __tablename__ = "subtopic_generation_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    main_topic_id = Column(Integer, ForeignKey("main_topics.id"), nullable=False, index=True)
    
    # 개인화 정보
    personalization_data = Column(JSON, nullable=True)
    generation_parameters = Column(JSON, nullable=True)
    
    # 요청 상태
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    
    # LLM 사용 정보
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    model_used = Column(String(100), nullable=True)
    
    # 결과 정보
    total_generated = Column(Integer, default=0)
    quality_score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # 관계 설정
    user = relationship("User")
    main_topic = relationship("MainTopic")
    generated_sub_topics = relationship("GeneratedSubTopic", back_populates="generation_request", cascade="all, delete-orphan")

    class Config:
        orm_mode = True