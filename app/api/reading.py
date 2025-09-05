from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database.database import get_db
from app.models import Article, UserArticleRead, User, CurriculumItem, LearningPath, SubTopic
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api", tags=["MVP Reading Management"])

# Response Models
class ReadResponse(BaseModel):
    article_id: str
    read_at: str

class CurrentArticleResponse(BaseModel):
    article_id: str
    title: str

class ProgressResponse(BaseModel):
    total_articles: int
    read_articles: int
    progress_percentage: int
    current_article: Optional[CurrentArticleResponse] = None


def get_user_id_from_token(authorization: str) -> str:
    """JWT 토큰에서 user_id 추출 (더미 구현)"""
    # TODO: 실제 JWT 토큰 파싱 로직 구현
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return "dummy_user_id"


@router.post("/articles/{article_id}/read", response_model=ReadResponse)
async def mark_article_read(
    article_id: str,
    db: Session = Depends(get_db),
    authorization: str = Header()
):
    """글 읽음 처리"""
    user_id = get_user_id_from_token(authorization)
    
    # 글 존재 확인
    article = db.query(Article).filter(Article.article_id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 이미 읽은 기록이 있는지 확인
    existing_read = db.query(UserArticleRead).filter(
        UserArticleRead.user_id == user_id,
        UserArticleRead.article_id == article_id
    ).first()
    
    if existing_read:
        # 이미 읽은 경우 시간만 업데이트
        existing_read.read_at = datetime.utcnow()
        read_record = existing_read
    else:
        # 새로운 읽음 기록 생성
        read_record = UserArticleRead(
            user_id=user_id,
            article_id=article_id,
            read_at=datetime.utcnow()
        )
        db.add(read_record)
    
    db.commit()
    db.refresh(read_record)
    
    return ReadResponse(
        article_id=read_record.article_id,
        read_at=read_record.read_at.isoformat() + "Z"
    )


@router.get("/users/{user_id}/progress", response_model=ProgressResponse)
async def get_user_progress(
    user_id: str,
    sub_topic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    authorization: str = Header()
):
    """사용자 진행률 조회"""
    token_user_id = get_user_id_from_token(authorization)
    
    # 본인의 진행률만 조회 가능 (추후 권한 체크 로직 추가)
    if user_id != token_user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    if sub_topic_id:
        # 특정 소주제의 진행률
        # 해당 소주제의 모든 글 수 계산
        total_articles = db.query(Article).filter(Article.sub_topic_id == sub_topic_id).count()
        
        # 읽은 글 수 계산
        read_articles = db.query(UserArticleRead).join(Article).filter(
            UserArticleRead.user_id == user_id,
            Article.sub_topic_id == sub_topic_id
        ).count()
        
        # 다음 읽을 글 찾기
        read_article_ids = db.query(UserArticleRead.article_id).filter(
            UserArticleRead.user_id == user_id
        ).subquery()
        
        next_article = db.query(Article).filter(
            Article.sub_topic_id == sub_topic_id,
            ~Article.article_id.in_(read_article_ids)
        ).first()
        
    else:
        # 전체 진행률
        total_articles = db.query(Article).count()
        read_articles = db.query(UserArticleRead).filter(
            UserArticleRead.user_id == user_id
        ).count()
        
        # 다음 읽을 글 찾기 (전체에서)
        read_article_ids = db.query(UserArticleRead.article_id).filter(
            UserArticleRead.user_id == user_id
        ).subquery()
        
        next_article = db.query(Article).filter(
            ~Article.article_id.in_(read_article_ids)
        ).first()
    
    progress_percentage = int((read_articles / total_articles * 100)) if total_articles > 0 else 0
    
    current_article = None
    if next_article:
        current_article = CurrentArticleResponse(
            article_id=next_article.article_id,
            title=next_article.title
        )
    
    return ProgressResponse(
        total_articles=total_articles,
        read_articles=read_articles,
        progress_percentage=progress_percentage,
        current_article=current_article
    )