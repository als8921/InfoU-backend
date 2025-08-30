from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import asyncio
from typing import Dict, Any

from app.database.database import get_db
from app.config import settings

router = APIRouter(
    prefix="",
    tags=["Health & Metadata"]
)


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    헬스체크 엔드포인트
    데이터베이스 연결, 서비스 상태 등을 확인하여 반환
    """
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": "disconnected",
            "llm_providers": []
        },
        "metrics": {
            "avg_response_time": "0ms",
            "active_sessions": 0,
            "generation_queue": 0
        }
    }
    
    # 데이터베이스 연결 상태 확인
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = "disconnected"
        health_status["status"] = "degraded"
    
    # LLM 프로바이더 상태 확인
    available_providers = []
    if settings.openai_api_key:
        available_providers.append("openai")
    if settings.anthropic_api_key:
        available_providers.append("anthropic")
    
    health_status["services"]["llm_providers"] = available_providers
    
    # LLM 프로바이더가 없으면 제한된 상태로 설정
    if not available_providers:
        health_status["status"] = "limited"
    
    return health_status