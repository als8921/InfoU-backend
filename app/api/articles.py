from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import get_db
from app.models import Article, CurriculumItem, UserArticleRead, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api", tags=["MVP Articles"])

# Response Models
class ArticleResponse(BaseModel):
    article_id: str
    title: str
    body: str
    level_code: str
    curriculum_item_id: str
    is_read: Optional[bool] = None

class ArticleNavigationResponse(BaseModel):
    article_id: str
    title: str
    curriculum_item_id: str

class ReadResponse(BaseModel):
    article_id: str
    read_at: str


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """글 상세 조회"""
    article = db.query(Article).filter(Article.article_id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    response = ArticleResponse(
        article_id=article.article_id,
        title=article.title,
        body=article.body,
        level_code=article.level_code,
        curriculum_item_id=article.curriculum_item_id
    )
    
    # 로그인 사용자인 경우 읽음 상태 확인
    if authorization and authorization.startswith("Bearer "):
        # TODO: JWT 토큰 파싱하여 user_id 추출
        # 현재는 더미 구현
        user_id = "dummy_user_id"  
        
        read_record = db.query(UserArticleRead).filter(
            UserArticleRead.user_id == user_id,
            UserArticleRead.article_id == article_id
        ).first()
        
        response.is_read = read_record is not None
    
    return response


@router.get("/articles/{article_id}/next", response_model=Optional[ArticleNavigationResponse])
async def get_next_article(article_id: str, db: Session = Depends(get_db)):
    """다음 글 조회"""
    # 현재 글 조회
    current_article = db.query(Article).filter(Article.article_id == article_id).first()
    if not current_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 현재 커리큘럼 아이템 조회
    current_curriculum = db.query(CurriculumItem).filter(
        CurriculumItem.curriculum_item_id == current_article.curriculum_item_id
    ).first()
    
    if not current_curriculum:
        return None
    
    # 같은 학습 경로에서 다음 순서의 커리큘럼 아이템 찾기
    next_curriculum = db.query(CurriculumItem).filter(
        CurriculumItem.path_id == current_curriculum.path_id,
        CurriculumItem.sort_order > current_curriculum.sort_order
    ).order_by(CurriculumItem.sort_order).first()
    
    if not next_curriculum:
        return None
    
    # 다음 커리큘럼 아이템의 같은 레벨 글 찾기
    next_article = db.query(Article).filter(
        Article.curriculum_item_id == next_curriculum.curriculum_item_id,
        Article.level_code == current_article.level_code
    ).first()
    
    if not next_article:
        return None
    
    return ArticleNavigationResponse(
        article_id=next_article.article_id,
        title=next_article.title,
        curriculum_item_id=next_article.curriculum_item_id
    )


@router.get("/articles/{article_id}/previous", response_model=Optional[ArticleNavigationResponse])
async def get_previous_article(article_id: str, db: Session = Depends(get_db)):
    """이전 글 조회"""
    # 현재 글 조회
    current_article = db.query(Article).filter(Article.article_id == article_id).first()
    if not current_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 현재 커리큘럼 아이템 조회
    current_curriculum = db.query(CurriculumItem).filter(
        CurriculumItem.curriculum_item_id == current_article.curriculum_item_id
    ).first()
    
    if not current_curriculum:
        return None
    
    # 같은 학습 경로에서 이전 순서의 커리큘럼 아이템 찾기
    previous_curriculum = db.query(CurriculumItem).filter(
        CurriculumItem.path_id == current_curriculum.path_id,
        CurriculumItem.sort_order < current_curriculum.sort_order
    ).order_by(CurriculumItem.sort_order.desc()).first()
    
    if not previous_curriculum:
        return None
    
    # 이전 커리큘럼 아이템의 같은 레벨 글 찾기
    previous_article = db.query(Article).filter(
        Article.curriculum_item_id == previous_curriculum.curriculum_item_id,
        Article.level_code == current_article.level_code
    ).first()
    
    if not previous_article:
        return None
    
    return ArticleNavigationResponse(
        article_id=previous_article.article_id,
        title=previous_article.title,
        curriculum_item_id=previous_article.curriculum_item_id
    )