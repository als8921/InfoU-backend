from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # SQLite를 기본 데이터베이스로 사용
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./infou.db")
    
    class Config:
        env_file = ".env"

settings = Settings()

# SQLite 데이터베이스 엔진 생성
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite 전용 설정
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
