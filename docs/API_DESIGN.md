# 📖 InfoU MVP API 설계 문서

## 개요

휴대폰으로 틈틈이 배우는 학습 플랫폼의 MVP 버전 API입니다.
핵심 학습 기능만 포함한 간소화된 REST API를 제공합니다.

---

## 🎯 MVP 핵심 기능

1. **주제 탐색**: 대주제 → 소주제 선택
2. **학습 경로**: 다양한 학습 경로 중 선택
3. **글 읽기**: 순차적 글 읽기 및 네비게이션
4. **읽음 관리**: 읽은 글 추적
5. **AI 컨텐츠 생성**: 소주제, 커리큘럼, 글 자동 생성

---

## 📋 API 엔드포인트 목록

| Method                         | Endpoint                                       | 설명                     |
| ------------------------------ | ---------------------------------------------- | ------------------------ |
| **MainTopic (대주제)**         |
| GET                            | `/api/main-topics`                             | 대주제 목록 조회         |
| **SubTopic (소주제)**          |
| GET                            | `/api/main-topics/{id}/sub-topics`             | 소주제 목록 조회         |
| POST                           | `/api/main-topics/{id}/sub-topics/generate`    | AI 소주제 생성           |
| **LearningPath (학습경로)**    |
| GET                            | `/api/sub-topics/{id}/learning-paths`          | 학습 경로 목록 조회      |
| POST                           | `/api/sub-topics/{id}/learning-paths/generate` | AI 커리큘럼 생성         |
| GET                            | `/api/learning-paths/{id}`                     | 특정 학습 경로 상세 조회 |
| **CurriculumItem (커리큘럼)**  |
| GET                            | `/api/learning-paths/{id}/curriculum-items`    | 커리큘럼 아이템 목록     |
| **Article (글)**               |
| GET                            | `/api/curriculum-items/{id}/articles`          | 난이도별 글 목록 조회    |
| POST                           | `/api/curriculum-items/{id}/articles/generate` | AI 글 생성               |
| GET                            | `/api/articles/{id}`                           | 글 상세 조회             |
| GET                            | `/api/articles/{id}/next`                      | 다음 글 조회             |
| GET                            | `/api/articles/{id}/previous`                  | 이전 글 조회             |
| **UserArticleRead (읽음기록)** |
| POST                           | `/api/articles/{id}/read`                      | 글 읽음 처리             |
| GET                            | `/api/users/{id}/progress`                     | 사용자 진행률 조회       |
| **Level (난이도)**             |
| GET                            | `/api/levels`                                  | 난이도 목록 조회         |

---

## 🏗️ API 상세 명세

### 1. MainTopic (대주제)

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

---

### 2. SubTopic (소주제)

#### 2.1 소주제 목록 조회

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

#### 2.2 AI 소주제 생성

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

### 3. LearningPath (학습경로)

#### 3.1 학습 경로 목록 조회

```
GET /api/sub-topics/{sub_topic_id}/learning-paths
Response: [
  {
    "path_id": "path_101",
    "title": "머신러닝 기초 과정",
    "description": "초보자를 위한 차근차근 학습",
    "curriculum_count": 8,
    "estimated_hours": 12
  },
  {
    "path_id": "path_102",
    "title": "머신러닝 실무 과정",
    "description": "프로젝트 중심의 실전 학습",
    "curriculum_count": 6,
    "estimated_hours": 18
  },
  {
    "path_id": "path_103",
    "title": "머신러닝 빠른 훑어보기",
    "description": "핵심만 빠르게 익히기",
    "curriculum_count": 4,
    "estimated_hours": 6
  }
]
```

#### 3.2 특정 학습 경로 상세 조회

```
GET /api/learning-paths/{path_id}
Response: {
  "path_id": "path_101",
  "title": "머신러닝 기초 과정",
  "description": "초보자를 위한 차근차근 학습",
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

#### 3.3 AI 커리큘럼 생성

```
POST /api/sub-topics/{sub_topic_id}/learning-paths/generate
Request: {
  "learning_objective": "머신러닝 기초 개념 학습",
  "difficulty": "beginner",
  "item_count": 5
}
Response: {
  "path_id": "path_102",
  "title": "머신러닝 기초 학습 과정",
  "curriculum_items": [
    {
      "curriculum_item_id": "item_10",
      "title": "머신러닝 소개",
      "sort_order": 1
    },
    {
      "curriculum_item_id": "item_11",
      "title": "데이터와 알고리즘",
      "sort_order": 2
    }
  ]
}
```

---

### 4. CurriculumItem (커리큘럼)

#### 4.1 커리큘럼 아이템 목록 조회

```
GET /api/learning-paths/{path_id}/curriculum-items
Response: [
  {
    "curriculum_item_id": "item_1",
    "title": "머신러닝이란?",
    "sort_order": 1,
    "has_articles": true
  },
  {
    "curriculum_item_id": "item_2",
    "title": "지도학습과 비지도학습",
    "sort_order": 2,
    "has_articles": true
  }
]
```

---

### 5. Article (글)

#### 5.1 난이도별 글 목록 조회

```
GET /api/curriculum-items/{curriculum_item_id}/articles
Query Parameters:
  - level: "beginner" | "intermediate" | "expert" (optional)
Response: [
  {
    "article_id": "art_101",
    "level_code": "beginner",
    "title": "머신러닝 기초 - 입문자용",
    "preview": "머신러닝은 컴퓨터가 데이터로부터..."
  },
  {
    "article_id": "art_102",
    "level_code": "intermediate",
    "title": "머신러닝 심화 - 중급자용",
    "preview": "회귀분석과 분류 알고리즘의 차이점..."
  },
  {
    "article_id": "art_103",
    "level_code": "expert",
    "title": "머신러닝 고급 - 전문가용",
    "preview": "복잡한 신경망 구조와 최적화 기법..."
  }
]
```

#### 5.2 글 상세 조회

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

#### 5.3 다음 글 조회

```
GET /api/articles/{article_id}/next
Query Parameters:
  - level: "beginner" | "intermediate" | "expert" (optional, 현재 글과 동일 레벨)
Response: {
  "article_id": "art_102",
  "title": "지도학습과 비지도학습",
  "curriculum_item_id": "item_2",
  "level_code": "beginner"
} | null
```

#### 5.4 이전 글 조회

```
GET /api/articles/{article_id}/previous
Query Parameters:
  - level: "beginner" | "intermediate" | "expert" (optional, 현재 글과 동일 레벨)
Response: {
  "article_id": "art_100",
  "title": "AI의 역사",
  "curriculum_item_id": "item_0",
  "level_code": "beginner"
} | null
```

---

#### 5.5 AI 글 생성

```
POST /api/curriculum-items/{curriculum_item_id}/articles/generate
Request: {
  "level": "beginner",
  "content_style": "concise",
  "word_count": 300
}
Response: {
  "article_id": "art_201",
  "title": "머신러닝이란?",
  "body": "머신러닝은 컴퓨터가 명시적으로 프로그래밍되지 않고도 데이터로부터 학습할 수 있게 하는 인공지능의 한 분야입니다...",
  "level_code": "beginner",
  "curriculum_item_id": "item_1"
}
```

---

### 6. UserArticleRead (읽음기록)

#### 6.1 글 읽음 처리

```
POST /api/articles/{article_id}/read
Headers: Authorization: Bearer {token}
Response: {
  "article_id": "art_101",
  "read_at": "2024-01-15T10:30:00Z"
}
```

#### 6.2 사용자 진행률 조회

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

### 7. Level (난이도)

#### 7.1 난이도 목록 조회

```
GET /api/levels
Response: [
  {
    "level_code": "beginner",
    "name": "입문자",
    "description": "기초부터 차근차근"
  },
  {
    "level_code": "intermediate",
    "name": "중급자",
    "description": "실무 적용 가능한 수준"
  },
  {
    "level_code": "expert",
    "name": "전문가",
    "description": "고급 이론과 최신 동향"
  }
]
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
2. **2단계**: 학습 경로 선택 API (GET learning-paths, learning-paths/{id})
3. **3단계**: 글 읽기 API (GET articles, next/previous)
4. **4단계**: 읽음 관리 API (POST read, GET progress)
5. **5단계**: AI 소주제 생성 API (POST sub-topics/generate)
6. **6단계**: AI 커리큘럼 생성 API (POST learning-paths/generate)
7. **7단계**: AI 글 생성 API (POST articles/generate)
