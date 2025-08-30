#!/usr/bin/env python3
"""
API 테스트 스크립트
Phase 1 구현 완료 후 API 엔드포인트 테스트
"""

import sys
import os
sys.path.append('.')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_levels():
    """난이도 API 테스트"""
    print("🧪 Testing Levels API...")
    
    # 기본 난이도 조회
    response = client.get("/levels")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    print(f"   ✅ GET /levels - {len(data)} levels found")
    
    # 통계 포함 난이도 조회
    response = client.get("/levels/with-stats")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    print(f"   ✅ GET /levels/with-stats - {len(data)} levels with stats")
    
    # 특정 난이도 조회
    response = client.get("/levels/absolute_beginner")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "absolute_beginner"
    assert data["name"] == "완전 초심자"
    print(f"   ✅ GET /levels/absolute_beginner - {data['name']}")


def test_main_topics():
    """대주제 API 테스트"""
    print("🧪 Testing Main Topics API...")
    
    # 페이징된 대주제 조회
    response = client.get("/main-topics?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 8
    assert len(data["items"]) == 5
    print(f"   ✅ GET /main-topics - {data['total']} total topics, showing {len(data['items'])}")
    
    # 특정 난이도별 대주제 조회
    response = client.get("/main-topics/by-level/beginner")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ GET /main-topics/by-level/beginner - {len(data)} topics found")
    
    # 특정 대주제 상세 조회
    response = client.get("/main-topics/1")
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    print(f"   ✅ GET /main-topics/1 - {data['title']}")


def test_curated_sub_topics():
    """큐레이션 소주제 API 테스트"""
    print("🧪 Testing Curated Sub Topics API...")
    
    # 페이징된 소주제 조회
    response = client.get("/sub-topics/curated?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 9
    assert len(data["items"]) == 5
    print(f"   ✅ GET /sub-topics/curated - {data['total']} total sub-topics, showing {len(data['items'])}")
    
    # 특정 난이도별 소주제 조회
    response = client.get("/sub-topics/curated/by-level/beginner")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ GET /sub-topics/curated/by-level/beginner - {len(data)} sub-topics found")
    
    # 특정 대주제별 소주제 조회
    response = client.get("/sub-topics/curated/by-main-topic/1")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ GET /sub-topics/curated/by-main-topic/1 - {len(data)} sub-topics found")
    
    # 특정 소주제 상세 조회
    response = client.get("/sub-topics/curated/1")
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    assert "main_topic" in data
    print(f"   ✅ GET /sub-topics/curated/1 - {data['title']}")


def main():
    """전체 API 테스트 실행"""
    print("🚀 Starting Phase 1 API Tests...\n")
    
    try:
        test_levels()
        print()
        test_main_topics()
        print()
        test_curated_sub_topics()
        
        print("\n🎉 All API tests passed successfully!")
        print("\n📊 Phase 1 Implementation Summary:")
        print("   ✅ Core data models (Level, MainTopic, CuratedSubTopic)")
        print("   ✅ SQLite database with WAL mode and optimizations")
        print("   ✅ Alembic migrations")
        print("   ✅ Seed data (5 levels, 8 main topics, 9 curated sub-topics)")
        print("   ✅ Pydantic schemas for all models")
        print("   ✅ RESTful APIs with pagination")
        print("   ✅ SQLite-optimized queries and indexing")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()