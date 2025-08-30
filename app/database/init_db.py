from app.database.database import engine, Base
from app.models.user import User

def init_db():
    """데이터베이스 테이블을 생성합니다."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("데이터베이스 테이블이 생성되었습니다.")
