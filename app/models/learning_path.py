from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class LearningPath(Base):
    __tablename__ = "learning_paths"

    path_id = Column(String, primary_key=True)
    sub_topic_id = Column(Integer, ForeignKey("sub_topics.sub_topic_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean)  # 선택: 기본 경로 표시가 필요할 때만 사용
    
    # 관계 설정
    sub_topic = relationship("SubTopic", back_populates="learning_paths")
    curriculum_items = relationship("CurriculumItem", back_populates="learning_path", cascade="all, delete-orphan")