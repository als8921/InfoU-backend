from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class UserArticleRead(Base):
    __tablename__ = "user_article_reads"

    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True, nullable=False)
    article_id = Column(String, ForeignKey("articles.article_id"), primary_key=True, nullable=False)
    read_at = Column(DateTime)
    
    # 관계 설정
    user = relationship("User", back_populates="article_reads")
    article = relationship("Article", back_populates="user_reads")
    
    __table_args__ = (
        Index('idx_user_read_at', 'user_id', 'read_at'),
    )