from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Dict, Any, List
import json

from app.database.database import get_db, engine
from app.config import settings

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


@router.post("/query", dependencies=[Depends(is_debug_enabled)])
async def execute_query(
    query_data: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """SQL 쿼리 직접 실행 (SELECT만 허용)"""
    try:
        query = query_data.get("query", "").strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # 보안을 위해 SELECT 쿼리만 허용
        if not query.upper().startswith("SELECT"):
            raise HTTPException(
                status_code=400, 
                detail="Only SELECT queries are allowed for security reasons"
            )
        
        result = db.execute(text(query))
        
        if result.returns_rows:
            columns = result.keys()
            rows = result.fetchall()
            
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
                "query": query,
                "columns": list(columns),
                "row_count": len(data),
                "data": data
            }
        else:
            return {
                "query": query,
                "message": "Query executed successfully (no rows returned)"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")


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