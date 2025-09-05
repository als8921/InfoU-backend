from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import Level
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Level"])

# Response Models
class LevelResponse(BaseModel):
    level_code: str
    name: str
    description: str


@router.get("/levels", response_model=List[LevelResponse])
async def get_levels(db: Session = Depends(get_db)):
    """난이도 목록 조회"""
    levels = db.query(Level).all()
    
    return [
        LevelResponse(
            level_code=level.level_code,
            name=level.name,
            description=level.description or ""
        )
        for level in levels
    ]