from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class Article(Base):
    __tablename__ = "articles"

    article_id = Column(String, primary_key=True)
    curriculum_item_id = Column(String, ForeignKey("curriculum_items.curriculum_item_id"), nullable=False)
    sub_topic_id = Column(Integer, ForeignKey("sub_topics.sub_topic_id"), nullable=False)
    level_code = Column(String, ForeignKey("levels.level_code"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    
    # 관계 설정
    curriculum_item = relationship("CurriculumItem", back_populates="articles")
    sub_topic = relationship("SubTopic", back_populates="articles")
    level = relationship("Level", back_populates="articles")
    user_reads = relationship("UserArticleRead", back_populates="article", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_sub_topic_level', 'sub_topic_id', 'level_code'),
        Index('idx_curriculum_item_level', 'curriculum_item_id', 'level_code', unique=True),
    )