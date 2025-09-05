from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.database import get_db
from app.models import Article, CurriculumItem, UserArticleRead, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Article"])

# Response Models
class ArticleListResponse(BaseModel):
    article_id: str
    level_code: str
    title: str
    preview: str

class ArticleDetailResponse(BaseModel):
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
    level_code: str

class GenerateArticleRequest(BaseModel):
    level: str
    content_style: str
    word_count: int

class GenerateArticleResponse(BaseModel):
    article_id: str
    title: str
    body: str
    level_code: str
    curriculum_item_id: str


@router.get("/curriculum-items/{curriculum_item_id}/articles", response_model=List[ArticleListResponse])
async def get_articles_by_curriculum_item(
    curriculum_item_id: str,
    level: Optional[str] = Query(None, description="beginner | intermediate | expert"),
    db: Session = Depends(get_db)
):
    """난이도별 글 목록 조회"""
    # 커리큘럼 아이템 존재 확인
    curriculum_item = db.query(CurriculumItem).filter(
        CurriculumItem.curriculum_item_id == curriculum_item_id
    ).first()
    if not curriculum_item:
        raise HTTPException(status_code=404, detail="Curriculum item not found")
    
    # 글 조회 쿼리
    query = db.query(Article).filter(Article.curriculum_item_id == curriculum_item_id)
    
    # 레벨 필터링
    if level:
        query = query.filter(Article.level_code == level)
    
    articles = query.all()
    
    return [
        ArticleListResponse(
            article_id=article.article_id,
            level_code=article.level_code,
            title=article.title,
            preview=article.body[:100] + "..." if len(article.body) > 100 else article.body
        )
        for article in articles
    ]


@router.get("/articles/{article_id}", response_model=ArticleDetailResponse)
async def get_article(
    article_id: str, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """글 상세 조회"""
    article = db.query(Article).filter(Article.article_id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    response = ArticleDetailResponse(
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
async def get_next_article(
    article_id: str, 
    level: Optional[str] = Query(None, description="beginner | intermediate | expert"),
    db: Session = Depends(get_db)
):
    """다음 글 조회"""
    # 현재 글 조회
    current_article = db.query(Article).filter(Article.article_id == article_id).first()
    if not current_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 레벨이 지정되지 않으면 현재 글과 동일한 레벨 사용
    target_level = level or current_article.level_code
    
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
    
    # 다음 커리큘럼 아이템의 지정된 레벨 글 찾기
    next_article = db.query(Article).filter(
        Article.curriculum_item_id == next_curriculum.curriculum_item_id,
        Article.level_code == target_level
    ).first()
    
    if not next_article:
        return None
    
    return ArticleNavigationResponse(
        article_id=next_article.article_id,
        title=next_article.title,
        curriculum_item_id=next_article.curriculum_item_id,
        level_code=next_article.level_code
    )


@router.get("/articles/{article_id}/previous", response_model=Optional[ArticleNavigationResponse])
async def get_previous_article(
    article_id: str,
    level: Optional[str] = Query(None, description="beginner | intermediate | expert"),
    db: Session = Depends(get_db)
):
    """이전 글 조회"""
    # 현재 글 조회
    current_article = db.query(Article).filter(Article.article_id == article_id).first()
    if not current_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 레벨이 지정되지 않으면 현재 글과 동일한 레벨 사용
    target_level = level or current_article.level_code
    
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
    
    # 이전 커리큘럼 아이템의 지정된 레벨 글 찾기
    previous_article = db.query(Article).filter(
        Article.curriculum_item_id == previous_curriculum.curriculum_item_id,
        Article.level_code == target_level
    ).first()
    
    if not previous_article:
        return None
    
    return ArticleNavigationResponse(
        article_id=previous_article.article_id,
        title=previous_article.title,
        curriculum_item_id=previous_article.curriculum_item_id,
        level_code=previous_article.level_code
    )


@router.post("/curriculum-items/{curriculum_item_id}/articles/generate", response_model=GenerateArticleResponse)
async def generate_article(
    curriculum_item_id: str,
    request: GenerateArticleRequest,
    db: Session = Depends(get_db)
):
    """AI 글 생성"""
    # 커리큘럼 아이템 존재 확인
    curriculum_item = db.query(CurriculumItem).filter(
        CurriculumItem.curriculum_item_id == curriculum_item_id
    ).first()
    if not curriculum_item:
        raise HTTPException(status_code=404, detail="Curriculum item not found")
    
    # TODO: 실제 AI 생성 로직 구현 필요
    # 더미 글 생성
    import uuid
    article_id = f"art_{uuid.uuid4().hex[:8]}"
    
    # 더미 컨텐츠 생성
    level_names = {
        "beginner": "기초",
        "intermediate": "중급",
        "expert": "고급"
    }
    
    title = f"{curriculum_item.title} - {level_names.get(request.level, '기본')}"
    body = f"""
{curriculum_item.title}에 대한 {level_names.get(request.level, '기본')} 수준의 학습 내용입니다.

이 글은 {request.content_style} 스타일로 작성되었으며, 약 {request.word_count}자 내외로 구성되어 있습니다.

TODO: 실제 AI로 생성된 고품질 학습 컨텐츠가 이 위치에 들어갑니다.

주요 학습 목표:
1. {curriculum_item.title}의 핵심 개념 이해
2. 실무 적용 방법 학습
3. 관련 기술과의 연관성 파악

이 내용을 통해 학습자는 {curriculum_item.title}에 대한 체계적인 이해를 얻을 수 있습니다.
""".strip()
    
    new_article = Article(
        article_id=article_id,
        curriculum_item_id=curriculum_item_id,
        sub_topic_id=curriculum_item.sub_topic_id,
        level_code=request.level,
        title=title,
        body=body
    )
    
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    return GenerateArticleResponse(
        article_id=new_article.article_id,
        title=new_article.title,
        body=new_article.body,
        level_code=new_article.level_code,
        curriculum_item_id=new_article.curriculum_item_id
    )