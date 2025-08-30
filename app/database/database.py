from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLite 최적화 설정
sqlite_connect_args = {
    "check_same_thread": False,  # SQLite 전용 설정
    "timeout": 20,  # 타임아웃 설정
}

# SQLite 데이터베이스 엔진 생성 (연결 풀링 및 최적화)
engine = create_engine(
    settings.database_url,
    connect_args=sqlite_connect_args,
    pool_size=20,  # 연결 풀 크기
    max_overflow=0,  # 추가 연결 허용하지 않음 (SQLite는 단일 파일이므로)
    pool_pre_ping=True,  # 연결 유효성 검사
    echo=settings.debug,  # 디버그 모드에서 SQL 로깅
)

# SQLite 최적화 이벤트 리스너
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """SQLite 연결 시 최적화 설정 적용"""
    cursor = dbapi_connection.cursor()
    # WAL 모드 활성화 (동시 읽기/쓰기 성능 향상)
    cursor.execute("PRAGMA journal_mode=WAL")
    # Foreign Key 제약조건 활성화
    cursor.execute("PRAGMA foreign_keys=ON")
    # 동기화 모드 설정 (성능 향상)
    cursor.execute("PRAGMA synchronous=NORMAL")
    # 캐시 크기 설정 (메모리 사용량 증가, 성능 향상)
    cursor.execute("PRAGMA cache_size=10000")
    # 임시 저장소를 메모리에 설정
    cursor.execute("PRAGMA temp_store=MEMORY")
    # mmap 크기 설정 (64MB)
    cursor.execute("PRAGMA mmap_size=67108864")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
