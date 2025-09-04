from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class SubTopic(Base):
    __tablename__ = "sub_topics"

    sub_topic_id = Column(Integer, primary_key=True, autoincrement=True)
    main_topic_id = Column(Integer, ForeignKey("main_topics.main_topic_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_type = Column(String, nullable=False)  # 'curated' | 'generated'
    
    # 관계 설정
    main_topic = relationship("MainTopic", back_populates="sub_topics")
    learning_paths = relationship("LearningPath", back_populates="sub_topic", cascade="all, delete-orphan")
    curriculum_items = relationship("CurriculumItem", back_populates="sub_topic", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="sub_topic", cascade="all, delete-orphan")