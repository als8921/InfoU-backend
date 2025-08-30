from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users

app = FastAPI(
    title="InfoU Backend API",
    description="InfoU 백엔드 API 서버",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "InfoU Backend API 서버에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
