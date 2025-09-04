from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    nickname = Column(String, nullable=False)
    email = Column(String, unique=True)
    
    # 관계 설정
    article_reads = relationship("UserArticleRead", back_populates="user", cascade="all, delete-orphan")
