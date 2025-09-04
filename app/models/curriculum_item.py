from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class CurriculumItem(Base):
    __tablename__ = "curriculum_items"

    curriculum_item_id = Column(String, primary_key=True)
    sub_topic_id = Column(Integer, ForeignKey("sub_topics.sub_topic_id"), nullable=False)
    path_id = Column(String, ForeignKey("learning_paths.path_id"), nullable=False)
    title = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False)
    
    # 관계 설정
    sub_topic = relationship("SubTopic", back_populates="curriculum_items")
    learning_path = relationship("LearningPath", back_populates="curriculum_items")
    articles = relationship("Article", back_populates="curriculum_item", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_path_sort_order', 'path_id', 'sort_order', unique=True),
        Index('idx_sub_topic_id', 'sub_topic_id'),
    )