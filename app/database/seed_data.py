"""
데이터베이스 시드 데이터 스크립트
5단계 난이도, 샘플 대주제, 큐레이션 소주제 데이터 삽입
"""

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models import Level, MainTopic, CuratedSubTopic


# 5단계 난이도 데이터
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


# 샘플 대주제 데이터
MAIN_TOPICS_DATA = [
    {
        "title": "웹 개발 기초",
        "description": "HTML, CSS, JavaScript를 활용한 웹 개발의 기본기",
        "level_code": "absolute_beginner"
    },
    {
        "title": "Python 프로그래밍",
        "description": "Python 언어의 기본 문법부터 고급 기능까지",
        "level_code": "beginner"
    },
    {
        "title": "데이터베이스 설계",
        "description": "관계형 데이터베이스의 설계 원칙과 최적화",
        "level_code": "intermediate"
    },
    {
        "title": "클라우드 아키텍처",
        "description": "AWS, GCP를 활용한 확장 가능한 시스템 설계",
        "level_code": "advanced"
    },
    {
        "title": "머신러닝 엔지니어링",
        "description": "프로덕션 환경에서의 ML 모델 운영과 최적화",
        "level_code": "expert"
    },
    {
        "title": "모바일 앱 개발",
        "description": "iOS, Android 네이티브 및 크로스 플랫폼 개발",
        "level_code": "intermediate"
    },
    {
        "title": "DevOps와 CI/CD",
        "description": "자동화된 배포 파이프라인과 인프라 관리",
        "level_code": "advanced"
    },
    {
        "title": "UI/UX 디자인",
        "description": "사용자 중심의 인터페이스 디자인 원칙",
        "level_code": "beginner"
    }
]


# 샘플 큐레이션 소주제 데이터
CURATED_SUB_TOPICS_DATA = [
    # 웹 개발 기초 (완전 초심자)
    {
        "title": "HTML 태그의 의미와 구조",
        "description": "HTML의 기본 태그들과 문서 구조를 이해하기",
        "main_topic_title": "웹 개발 기초",
        "keywords": ["HTML", "태그", "마크업", "구조"],
        "learning_objectives": ["HTML 태그의 역할 이해", "기본 웹페이지 구조 파악"],
        "prerequisites": ["컴퓨터 기본 사용법"],
        "estimated_duration_minutes": 45,
        "difficulty_score": 2
    },
    {
        "title": "CSS로 웹페이지 꾸미기",
        "description": "CSS 선택자와 속성을 활용한 스타일링",
        "main_topic_title": "웹 개발 기초",
        "keywords": ["CSS", "스타일링", "선택자", "디자인"],
        "learning_objectives": ["CSS 문법 이해", "기본 스타일 적용"],
        "prerequisites": ["HTML 기초"],
        "estimated_duration_minutes": 60,
        "difficulty_score": 3
    },
    
    # Python 프로그래밍 (초심자)
    {
        "title": "Python 변수와 데이터 타입",
        "description": "Python의 기본 데이터 타입과 변수 사용법",
        "main_topic_title": "Python 프로그래밍",
        "keywords": ["Python", "변수", "데이터타입", "기초"],
        "learning_objectives": ["변수 선언과 할당", "데이터 타입별 특징 이해"],
        "prerequisites": ["프로그래밍 개념"],
        "estimated_duration_minutes": 40,
        "difficulty_score": 2
    },
    {
        "title": "조건문과 반복문 활용",
        "description": "if문, for문, while문을 활용한 프로그램 제어",
        "main_topic_title": "Python 프로그래밍",
        "keywords": ["조건문", "반복문", "제어구조", "로직"],
        "learning_objectives": ["조건문 작성", "반복문 활용"],
        "prerequisites": ["Python 기초 문법"],
        "estimated_duration_minutes": 50,
        "difficulty_score": 4
    },
    
    # 데이터베이스 설계 (중급자)
    {
        "title": "정규화와 관계 설계",
        "description": "데이터베이스 정규화 과정과 테이블 간 관계 설정",
        "main_topic_title": "데이터베이스 설계",
        "keywords": ["정규화", "관계", "ERD", "데이터베이스"],
        "learning_objectives": ["정규화 원칙 이해", "효율적인 테이블 설계"],
        "prerequisites": ["SQL 기초", "데이터베이스 개념"],
        "estimated_duration_minutes": 80,
        "difficulty_score": 6
    },
    {
        "title": "인덱스 최적화 전략",
        "description": "쿼리 성능 향상을 위한 인덱스 설계와 최적화",
        "main_topic_title": "데이터베이스 설계",
        "keywords": ["인덱스", "최적화", "성능", "쿼리"],
        "learning_objectives": ["인덱스 설계 원칙", "성능 최적화 방법"],
        "prerequisites": ["SQL 숙련", "데이터베이스 운영 경험"],
        "estimated_duration_minutes": 70,
        "difficulty_score": 7
    },
    
    # 클라우드 아키텍처 (고급자)
    {
        "title": "마이크로서비스 패턴과 설계",
        "description": "마이크로서비스 아키텍처의 패턴과 설계 원칙",
        "main_topic_title": "클라우드 아키텍처",
        "keywords": ["마이크로서비스", "아키텍처", "패턴", "설계"],
        "learning_objectives": ["마이크로서비스 패턴 이해", "서비스 분해 전략"],
        "prerequisites": ["분산 시스템 이해", "클라우드 경험"],
        "estimated_duration_minutes": 90,
        "difficulty_score": 8
    },
    
    # 머신러닝 엔지니어링 (전문가)
    {
        "title": "MLOps 파이프라인 구축",
        "description": "프로덕션 환경에서의 ML 모델 배포와 모니터링",
        "main_topic_title": "머신러닝 엔지니어링",
        "keywords": ["MLOps", "파이프라인", "배포", "모니터링"],
        "learning_objectives": ["MLOps 프로세스 구축", "모델 모니터링 시스템"],
        "prerequisites": ["머신러닝 모델링", "DevOps 경험"],
        "estimated_duration_minutes": 120,
        "difficulty_score": 9
    },
    
    # UI/UX 디자인 (초심자)
    {
        "title": "사용자 경험 설계 원칙",
        "description": "사용자 중심 디자인의 기본 원칙과 방법론",
        "main_topic_title": "UI/UX 디자인",
        "keywords": ["UX", "사용자경험", "디자인원칙", "방법론"],
        "learning_objectives": ["UX 디자인 원칙 이해", "사용자 리서치 방법"],
        "prerequisites": ["디자인 기초 개념"],
        "estimated_duration_minutes": 55,
        "difficulty_score": 3
    }
]


def seed_levels(db: Session) -> dict:
    """난이도 데이터 시딩"""
    level_map = {}
    
    for level_data in LEVELS_DATA:
        # 기존 레벨이 있는지 확인
        existing_level = db.query(Level).filter(Level.code == level_data["code"]).first()
        if not existing_level:
            level = Level(**level_data)
            db.add(level)
            db.flush()  # ID 생성을 위해 flush
            level_map[level_data["code"]] = level.id
        else:
            level_map[level_data["code"]] = existing_level.id
    
    db.commit()
    return level_map


def seed_main_topics(db: Session, level_map: dict) -> dict:
    """대주제 데이터 시딩"""
    topic_map = {}
    
    for topic_data in MAIN_TOPICS_DATA:
        # 기존 주제가 있는지 확인
        existing_topic = db.query(MainTopic).filter(MainTopic.title == topic_data["title"]).first()
        if not existing_topic:
            topic = MainTopic(
                title=topic_data["title"],
                description=topic_data["description"],
                level_id=level_map[topic_data["level_code"]]
            )
            db.add(topic)
            db.flush()
            topic_map[topic_data["title"]] = topic.id
        else:
            topic_map[topic_data["title"]] = existing_topic.id
    
    db.commit()
    return topic_map


def seed_curated_sub_topics(db: Session, level_map: dict, topic_map: dict):
    """큐레이션 소주제 데이터 시딩"""
    
    for sub_topic_data in CURATED_SUB_TOPICS_DATA:
        # 기존 소주제가 있는지 확인
        existing_sub_topic = db.query(CuratedSubTopic).filter(
            CuratedSubTopic.title == sub_topic_data["title"]
        ).first()
        
        if not existing_sub_topic:
            # 주제의 레벨 찾기
            main_topic = db.query(MainTopic).filter(
                MainTopic.title == sub_topic_data["main_topic_title"]
            ).first()
            
            if main_topic:
                sub_topic = CuratedSubTopic(
                    title=sub_topic_data["title"],
                    description=sub_topic_data["description"],
                    main_topic_id=topic_map[sub_topic_data["main_topic_title"]],
                    level_id=main_topic.level_id,
                    keywords=sub_topic_data["keywords"],
                    learning_objectives=sub_topic_data["learning_objectives"],
                    prerequisites=sub_topic_data["prerequisites"],
                    estimated_duration_minutes=sub_topic_data["estimated_duration_minutes"],
                    difficulty_score=sub_topic_data["difficulty_score"]
                )
                db.add(sub_topic)
    
    db.commit()


def seed_database():
    """전체 시드 데이터 실행"""
    db = SessionLocal()
    try:
        print("🌱 데이터베이스 시딩 시작...")
        
        # 1. 레벨 시딩
        print("📊 난이도 데이터 삽입...")
        level_map = seed_levels(db)
        print(f"✅ {len(LEVELS_DATA)}개 난이도 데이터 완료")
        
        # 2. 대주제 시딩
        print("📚 대주제 데이터 삽입...")
        topic_map = seed_main_topics(db, level_map)
        print(f"✅ {len(MAIN_TOPICS_DATA)}개 대주제 데이터 완료")
        
        # 3. 큐레이션 소주제 시딩
        print("🎯 큐레이션 소주제 데이터 삽입...")
        seed_curated_sub_topics(db, level_map, topic_map)
        print(f"✅ {len(CURATED_SUB_TOPICS_DATA)}개 소주제 데이터 완료")
        
        print("🎉 데이터베이스 시딩 완료!")
        
    except Exception as e:
        print(f"❌ 시딩 실패: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()