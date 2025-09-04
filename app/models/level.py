from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class Level(Base):
    __tablename__ = "levels"

    level_code = Column(String, primary_key=True)  # 'beginner' | 'intermediate' | 'expert'
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # 관계 설정
    articles = relationship("Article", back_populates="level", cascade="all, delete-orphan")