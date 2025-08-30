# InfoU Backend

FastAPI 기반의 백엔드 API 서버입니다.

## 설치 및 실행

### 1. 가상환경 활성화

```bash
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate     # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 실제 값으로 수정
```

### 4. 서버 실행

```bash
# 개발 모드로 실행
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
InfoU-backend/
├── app/
│   ├── api/           # API 라우터
│   ├── models/        # SQLAlchemy 모델
│   ├── schemas/       # Pydantic 스키마
│   └── database/      # 데이터베이스 설정
├── main.py            # 메인 애플리케이션
├── requirements.txt   # 의존성 목록
├── env.example        # 환경 변수 예시
└── README.md          # 프로젝트 설명
```

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/api/` 디렉토리에 라우터 파일 생성
2. `main.py`에 라우터 등록
3. 필요한 스키마와 모델 정의

### 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 스키마를 관리할 수 있습니다.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.
