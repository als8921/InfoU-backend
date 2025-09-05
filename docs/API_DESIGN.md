# 📖 InfoU MVP API 설계 문서

## 개요

휴대폰으로 틈틈이 배우는 학습 플랫폼의 MVP 버전 API입니다.
핵심 학습 기능만 포함한 간소화된 REST API를 제공합니다.

---

## 🎯 MVP 핵심 기능

1. **주제 탐색**: 대주제 → 소주제 선택
2. **학습 경로**: 기본 학습 경로 제공
3. **글 읽기**: 순차적 글 읽기 및 네비게이션
4. **읽음 관리**: 읽은 글 추적

---

## 📋 API 엔드포인트 목록

| Method        | Endpoint                                    | 설명                |
| ------------- | ------------------------------------------- | ------------------- |
| **주제 관리** |
| GET           | `/api/main-topics`                          | 대주제 목록 조회    |
| GET           | `/api/main-topics/{id}/sub-topics`          | 소주제 목록 조회    |
| POST          | `/api/main-topics/{id}/sub-topics/generate` | AI 소주제 생성      |
| **학습 경로** |
| GET           | `/api/sub-topics/{id}/learning-path`        | 기본 학습 경로 조회 |
| **글 읽기**   |
| GET           | `/api/articles/{id}`                        | 글 상세 조회        |
| GET           | `/api/articles/{id}/next`                   | 다음 글 조회        |
| GET           | `/api/articles/{id}/previous`               | 이전 글 조회        |
| **읽음 관리** |
| POST          | `/api/articles/{id}/read`                   | 글 읽음 처리        |
| GET           | `/api/users/{id}/progress`                  | 사용자 진행률 조회  |

---

## 🏗️ API 상세 명세

### 1. 주제 관리

#### 1.1 대주제 목록 조회

```
GET /api/main-topics
Response: [
  {
    "main_topic_id": 1,
    "name": "인공지능",
    "description": "AI 기초부터 응용까지"
  }
]
```

#### 1.2 소주제 목록 조회

```
GET /api/main-topics/{main_topic_id}/sub-topics
Response: [
  {
    "sub_topic_id": 101,
    "name": "머신러닝 기초",
    "description": "ML 개념과 알고리즘",
    "source_type": "curated"
  }
]
```

#### 1.3 AI 소주제 생성

```
POST /api/main-topics/{main_topic_id}/sub-topics/generate
Request: { "topic_hint": "딥러닝" }
Response: {
  "sub_topic_id": 102,
  "name": "딥러닝 입문",
  "description": "신경망과 딥러닝 기초",
  "source_type": "generated"
}
```

---

### 2. 학습 경로

#### 2.1 기본 학습 경로 조회

```
GET /api/sub-topics/{sub_topic_id}/learning-path
Response: {
  "path_id": "path_101",
  "title": "머신러닝 기초 과정",
  "curriculum_items": [
    {
      "curriculum_item_id": "item_1",
      "title": "머신러닝이란?",
      "sort_order": 1
    },
    {
      "curriculum_item_id": "item_2",
      "title": "지도학습과 비지도학습",
      "sort_order": 2
    }
  ]
}
```

---

### 3. 글 읽기

#### 3.1 글 상세 조회

```
GET /api/articles/{article_id}
Headers: Authorization: Bearer {token} (optional)
Response: {
  "article_id": "art_101",
  "title": "머신러닝이란?",
  "body": "머신러닝은 컴퓨터가 데이터로부터 학습하는...",
  "level_code": "beginner",
  "curriculum_item_id": "item_1",
  "is_read": false  // 로그인 시에만
}
```

#### 3.2 다음 글 조회

```
GET /api/articles/{article_id}/next
Response: {
  "article_id": "art_102",
  "title": "지도학습과 비지도학습",
  "curriculum_item_id": "item_2"
} | null
```

#### 3.3 이전 글 조회

```
GET /api/articles/{article_id}/previous
Response: {
  "article_id": "art_100",
  "title": "AI의 역사",
  "curriculum_item_id": "item_0"
} | null
```

---

### 4. 읽음 관리

#### 4.1 글 읽음 처리

```
POST /api/articles/{article_id}/read
Headers: Authorization: Bearer {token}
Response: {
  "article_id": "art_101",
  "read_at": "2024-01-15T10:30:00Z"
}
```

#### 4.2 사용자 진행률 조회

```
GET /api/users/{user_id}/progress
Headers: Authorization: Bearer {token}
Query: ?sub_topic_id=101 (optional)
Response: {
  "total_articles": 10,
  "read_articles": 3,
  "progress_percentage": 30,
  "current_article": {
    "article_id": "art_104",
    "title": "다음 읽을 글"
  }
}
```

---

## 🚨 에러 응답

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "글을 찾을 수 없습니다"
  }
}
```

**주요 에러 코드:**

- `400`: 잘못된 요청
- `401`: 인증 필요
- `404`: 리소스 없음
- `500`: 서버 오류

---

## 🚀 MVP 구현 순서

1. **1단계**: 주제 조회 API (GET main-topics, sub-topics)
2. **2단계**: 글 읽기 API (GET articles, next/previous)
3. **3단계**: 읽음 관리 API (POST read, GET progress)
4. **4단계**: AI 생성 API (POST generate)
