from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """모든 사용자 목록을 반환합니다."""
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자 정보를 반환합니다."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """새로운 사용자를 생성합니다."""
    # 중복 사용자 확인
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="사용자명 또는 이메일이 이미 존재합니다")
    
    # 실제로는 비밀번호를 해시화해야 합니다
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # 실제로는 해시화된 비밀번호를 저장해야 합니다
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
