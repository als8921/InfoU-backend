from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# API 라우터들
from app.api import health, levels

app = FastAPI(
    title=settings.app_name,
    description="LLM 기반 개인화 소주제 생성 및 5단계 난이도별 동적 커리큘럼/아티클 생성을 지원하는 고성능 학습 API 서버",
    version=settings.app_version,
    debug=settings.debug
)

# CORS 미들웨어 설정
cors_origins = settings.cors_origins.split(",") if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(health.router)
app.include_router(levels.router)

@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} v{settings.app_version}에 오신 것을 환영합니다!",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
