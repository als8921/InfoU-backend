from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class MainTopic(Base):
    __tablename__ = "main_topics"

    main_topic_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # 관계 설정
    sub_topics = relationship("SubTopic", back_populates="main_topic", cascade="all, delete-orphan")