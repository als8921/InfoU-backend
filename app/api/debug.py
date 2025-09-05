from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

from app.database.database import get_db, engine
from app.config import settings
from app.models.user import User
from app.models.level import Level
from app.models.main_topic import MainTopic
from app.models.sub_topic import SubTopic
from app.models.learning_path import LearningPath
from app.models.curriculum_item import CurriculumItem
from app.models.article import Article
from app.models.user_article_read import UserArticleRead

router = APIRouter(
    prefix="/debug",
    tags=["Debug & Development"]
)


def is_debug_enabled():
    """디버그 모드인지 확인"""
    if not settings.debug:
        raise HTTPException(
            status_code=403, 
            detail="Debug endpoints are only available in development mode"
        )
    return True


@router.get("/tables", dependencies=[Depends(is_debug_enabled)])
async def list_tables(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """데이터베이스의 모든 테이블 목록 조회"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        return {
            "tables": tables,
            "total_count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")


@router.get("/tables/{table_name}", dependencies=[Depends(is_debug_enabled)])
async def get_table_info(table_name: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """특정 테이블의 구조 정보 조회"""
    try:
        inspector = inspect(engine)
        
        # 테이블 존재 확인
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # 테이블 구조 정보
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # 행 수 조회
        result = db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
        row_count = result.fetchone()[0]
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col["default"]) if col["default"] else None
                }
                for col in columns
            ],
            "primary_keys": primary_keys["constrained_columns"],
            "foreign_keys": [
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                }
                for fk in foreign_keys
            ],
            "indexes": [
                {
                    "name": idx["name"],
                    "columns": idx["column_names"],
                    "unique": idx["unique"]
                }
                for idx in indexes
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching table info: {str(e)}")


@router.get("/tables/{table_name}/data", dependencies=[Depends(is_debug_enabled)])
async def get_table_data(
    table_name: str, 
    limit: int = 100, 
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """특정 테이블의 데이터 조회"""
    try:
        inspector = inspect(engine)
        
        # 테이블 존재 확인
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # 전체 행 수 조회
        count_result = db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
        total_count = count_result.fetchone()[0]
        
        # 데이터 조회
        data_result = db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"))
        columns = data_result.keys()
        rows = data_result.fetchall()
        
        # 결과를 딕셔너리 형태로 변환
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # JSON 문자열인 경우 파싱 시도
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    try:
                        value = json.loads(value)
                    except:
                        pass
                row_dict[col] = value
            data.append(row_dict)
        
        return {
            "table_name": table_name,
            "total_count": total_count,
            "returned_count": len(data),
            "limit": limit,
            "offset": offset,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching table data: {str(e)}")



@router.get("/db-stats", dependencies=[Depends(is_debug_enabled)])
async def get_database_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """데이터베이스 전체 통계 정보"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        stats = {
            "database_url": settings.database_url,
            "total_tables": len(tables),
            "tables": {}
        }
        
        total_rows = 0
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                count = result.fetchone()[0]
                stats["tables"][table] = count
                total_rows += count
            except:
                stats["tables"][table] = "Error getting count"
        
        stats["total_rows"] = total_rows
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")


@router.delete("/tables/{table_name}", dependencies=[Depends(is_debug_enabled)])
async def clear_table(table_name: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    """특정 테이블의 모든 데이터 삭제 (개발용)"""
    try:
        inspector = inspect(engine)
        
        # 테이블 존재 확인
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # 데이터 삭제
        result = db.execute(text(f"DELETE FROM {table_name}"))
        db.commit()
        
        return {
            "message": f"All data from table '{table_name}' has been deleted",
            "table_name": table_name,
            "rows_affected": str(result.rowcount) if hasattr(result, 'rowcount') else "unknown"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing table: {str(e)}")


# 데이터 생성 API 엔드포인트들

@router.post("/data/users", dependencies=[Depends(is_debug_enabled)])
async def create_user(user_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """사용자 데이터 생성"""
    try:
        user = User(
            user_id=user_data.get("user_id") or str(uuid.uuid4()),
            nickname=user_data["nickname"],
            email=user_data.get("email")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "message": "User created successfully",
            "data": {
                "user_id": user.user_id,
                "nickname": user.nickname,
                "email": user.email
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")


@router.post("/data/levels", dependencies=[Depends(is_debug_enabled)])
async def create_level(level_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """난이도 데이터 생성"""
    try:
        level = Level(
            level_code=level_data["level_code"],
            name=level_data["name"],
            description=level_data.get("description")
        )
        db.add(level)
        db.commit()
        db.refresh(level)
        
        return {
            "message": "Level created successfully",
            "data": {
                "level_code": level.level_code,
                "name": level.name,
                "description": level.description
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating level: {str(e)}")


@router.post("/data/main-topics", dependencies=[Depends(is_debug_enabled)])
async def create_main_topic(topic_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """메인 토픽 데이터 생성"""
    try:
        main_topic = MainTopic(
            name=topic_data["name"],
            description=topic_data.get("description")
        )
        db.add(main_topic)
        db.commit()
        db.refresh(main_topic)
        
        return {
            "message": "Main topic created successfully",
            "data": {
                "main_topic_id": main_topic.main_topic_id,
                "name": main_topic.name,
                "description": main_topic.description
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating main topic: {str(e)}")


@router.post("/data/sub-topics", dependencies=[Depends(is_debug_enabled)])
async def create_sub_topic(topic_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """서브 토픽 데이터 생성"""
    try:
        sub_topic = SubTopic(
            main_topic_id=topic_data["main_topic_id"],
            name=topic_data["name"],
            description=topic_data.get("description"),
            source_type=topic_data.get("source_type", "curated")
        )
        db.add(sub_topic)
        db.commit()
        db.refresh(sub_topic)
        
        return {
            "message": "Sub topic created successfully",
            "data": {
                "sub_topic_id": sub_topic.sub_topic_id,
                "main_topic_id": sub_topic.main_topic_id,
                "name": sub_topic.name,
                "description": sub_topic.description,
                "source_type": sub_topic.source_type
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating sub topic: {str(e)}")


@router.post("/data/learning-paths", dependencies=[Depends(is_debug_enabled)])
async def create_learning_path(path_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """학습 경로 데이터 생성"""
    try:
        learning_path = LearningPath(
            path_id=path_data.get("path_id") or str(uuid.uuid4()),
            sub_topic_id=path_data["sub_topic_id"],
            title=path_data["title"],
            description=path_data.get("description"),
            is_default=path_data.get("is_default", False)
        )
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)
        
        return {
            "message": "Learning path created successfully",
            "data": {
                "path_id": learning_path.path_id,
                "sub_topic_id": learning_path.sub_topic_id,
                "title": learning_path.title,
                "description": learning_path.description,
                "is_default": learning_path.is_default
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating learning path: {str(e)}")


@router.post("/data/curriculum-items", dependencies=[Depends(is_debug_enabled)])
async def create_curriculum_item(item_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """커리큘럼 아이템 데이터 생성"""
    try:
        curriculum_item = CurriculumItem(
            curriculum_item_id=item_data.get("curriculum_item_id") or str(uuid.uuid4()),
            sub_topic_id=item_data["sub_topic_id"],
            path_id=item_data["path_id"],
            title=item_data["title"],
            sort_order=item_data["sort_order"]
        )
        db.add(curriculum_item)
        db.commit()
        db.refresh(curriculum_item)
        
        return {
            "message": "Curriculum item created successfully",
            "data": {
                "curriculum_item_id": curriculum_item.curriculum_item_id,
                "sub_topic_id": curriculum_item.sub_topic_id,
                "path_id": curriculum_item.path_id,
                "title": curriculum_item.title,
                "sort_order": curriculum_item.sort_order
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating curriculum item: {str(e)}")


@router.post("/data/articles", dependencies=[Depends(is_debug_enabled)])
async def create_article(article_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """아티클 데이터 생성"""
    try:
        article = Article(
            article_id=article_data.get("article_id") or str(uuid.uuid4()),
            curriculum_item_id=article_data["curriculum_item_id"],
            sub_topic_id=article_data["sub_topic_id"],
            level_code=article_data["level_code"],
            title=article_data["title"],
            body=article_data["body"]
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        
        return {
            "message": "Article created successfully",
            "data": {
                "article_id": article.article_id,
                "curriculum_item_id": article.curriculum_item_id,
                "sub_topic_id": article.sub_topic_id,
                "level_code": article.level_code,
                "title": article.title,
                "body": article.body[:100] + "..." if len(article.body) > 100 else article.body
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating article: {str(e)}")


@router.post("/data/user-article-reads", dependencies=[Depends(is_debug_enabled)])
async def create_user_article_read(read_data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """사용자 아티클 읽기 기록 생성"""
    try:
        user_read = UserArticleRead(
            user_id=read_data["user_id"],
            article_id=read_data["article_id"],
            read_at=datetime.fromisoformat(read_data.get("read_at", datetime.now().isoformat()))
        )
        db.add(user_read)
        db.commit()
        db.refresh(user_read)
        
        return {
            "message": "User article read record created successfully",
            "data": {
                "user_id": user_read.user_id,
                "article_id": user_read.article_id,
                "read_at": user_read.read_at.isoformat() if user_read.read_at else None
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user article read: {str(e)}")


# 참조 데이터 조회를 위한 헬퍼 엔드포인트들

@router.get("/reference/main-topics", dependencies=[Depends(is_debug_enabled)])
async def get_main_topics_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """메인 토픽 참조 데이터"""
    topics = db.query(MainTopic).all()
    return [{"id": t.main_topic_id, "name": t.name} for t in topics]


@router.get("/reference/sub-topics", dependencies=[Depends(is_debug_enabled)])
async def get_sub_topics_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """서브 토픽 참조 데이터"""
    topics = db.query(SubTopic).all()
    return [{"id": t.sub_topic_id, "name": t.name, "main_topic_id": t.main_topic_id} for t in topics]


@router.get("/reference/learning-paths", dependencies=[Depends(is_debug_enabled)])
async def get_learning_paths_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """학습 경로 참조 데이터"""
    paths = db.query(LearningPath).all()
    return [{"id": p.path_id, "title": p.title, "sub_topic_id": p.sub_topic_id} for p in paths]


@router.get("/reference/curriculum-items", dependencies=[Depends(is_debug_enabled)])
async def get_curriculum_items_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """커리큘럼 아이템 참조 데이터"""
    items = db.query(CurriculumItem).all()
    return [{"id": i.curriculum_item_id, "title": i.title, "sub_topic_id": i.sub_topic_id} for i in items]


@router.get("/reference/levels", dependencies=[Depends(is_debug_enabled)])
async def get_levels_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """레벨 참조 데이터"""
    levels = db.query(Level).all()
    return [{"code": l.level_code, "name": l.name} for l in levels]


@router.get("/reference/users", dependencies=[Depends(is_debug_enabled)])
async def get_users_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """사용자 참조 데이터"""
    users = db.query(User).all()
    return [{"id": u.user_id, "nickname": u.nickname} for u in users]


@router.get("/reference/articles", dependencies=[Depends(is_debug_enabled)])
async def get_articles_reference(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """아티클 참조 데이터"""
    articles = db.query(Article).all()
    return [{"id": a.article_id, "title": a.title, "level_code": a.level_code} for a in articles]