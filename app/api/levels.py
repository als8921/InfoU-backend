from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(
    prefix="/levels",
    tags=["Levels"]
)

# 5단계 난이도 정의 (PRD 기반)
LEVELS_DATA = [
    {
        "code": "absolute_beginner",
        "name": "완전 초심자",
        "description": "해당 분야를 처음 접하는 사람",
        "target_audience": "학생, 비전공자",
        "characteristics": ["용어 정의", "비유적 설명", "기초 개념"],
        "estimated_hours_per_week": 2,
        "order": 1
    },
    {
        "code": "beginner",
        "name": "초심자",
        "description": "기초 개념을 어느정도 이해한 사람",
        "target_audience": "기초 지식이 있는 학습자",
        "characteristics": ["기본 개념", "간단한 실습", "구체적 예제"],
        "estimated_hours_per_week": 3,
        "order": 2
    },
    {
        "code": "intermediate",
        "name": "중급자",
        "description": "기본적인 지식을 바탕으로 응용할 수 있는 사람",
        "target_audience": "어느정도 경험이 있는 학습자",
        "characteristics": ["실무 활용", "응용 문제", "프로젝트 기반"],
        "estimated_hours_per_week": 4,
        "order": 3
    },
    {
        "code": "advanced",
        "name": "고급자",
        "description": "전문적인 지식과 경험을 보유한 사람",
        "target_audience": "전문가, 실무진",
        "characteristics": ["심화 개념", "복잡한 문제해결", "최적화"],
        "estimated_hours_per_week": 5,
        "order": 4
    },
    {
        "code": "expert",
        "name": "전문가",
        "description": "해당 분야의 깊은 전문성을 가진 사람",
        "target_audience": "업계 전문가, 연구자",
        "characteristics": ["최신 기술", "연구 동향", "혁신적 접근"],
        "estimated_hours_per_week": 6,
        "order": 5
    }
]


@router.get("")
async def get_levels() -> Dict[str, List[Dict[str, Any]]]:
    """
    난이도 메타데이터 조회
    5단계 난이도 정보를 반환
    """
    return {"levels": LEVELS_DATA}


@router.get("/{level_code}")
async def get_level_by_code(level_code: str) -> Dict[str, Any]:
    """
    특정 난이도 코드로 상세 정보 조회
    """
    level = next((l for l in LEVELS_DATA if l["code"] == level_code), None)
    if not level:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Level not found")
    
    return level