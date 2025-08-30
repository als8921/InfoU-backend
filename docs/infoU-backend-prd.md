# 📄 InfoU 백엔드 PRD v1.0

## 1. 프로젝트 개요

- **목표:**  
  LLM 기반 개인화 소주제 생성 및 5단계 난이도별 동적 커리큘럼/아티클 생성을 지원하는 고성능 학습 API 서버

- **플랫폼/스택:**  
  FastAPI + PostgreSQL + SQLAlchemy + Alembic + Redis + Celery  
  LLM Integration: OpenAI GPT-4 / Anthropic Claude / 로컬 모델

- **핵심 특징:**
  - 비동기 LLM 콘텐츠 생성 (백그라운드 태스크)
  - 실시간 생성 상태 추적 (WebSocket)
  - 5단계 난이도 지원 (완전초심자 → 전문가)
  - 개인화 알고리즘 및 품질 관리 시스템

---

## 2. 핵심 기능 흐름

1. **대주제 조회** → 큐레이션된 메인 토픽
2. **소주제 생성/선택** → LLM 개인화 생성 + 큐레이션 혼합
3. **세션 생성** → 사용자별 학습 세션 관리
4. **백그라운드 생성** → 커리큘럼 & 아티클 비동기 생성
5. **실시간 상태 제공** → WebSocket을 통한 진행상황 업데이트
6. **아티클 제공** → 동적 생성된 학습 콘텐츠 서빙

---

## 3. API 엔드포인트

### 3.1 Health Check & Metadata

**헬스 체크**

```http
GET /health
```

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "llm_providers": ["openai", "anthropic"],
    "celery": "active_workers_3"
  },
  "metrics": {
    "avg_response_time": "145ms",
    "active_sessions": 42,
    "generation_queue": 5
  }
}
```

**난이도 메타데이터**

```http
GET /levels
```

```json
{
  "levels": [
    {
      "code": "absolute_beginner",
      "name": "완전 초심자",
      "description": "해당 분야를 처음 접하는 사람",
      "target_audience": "학생, 비전공자",
      "characteristics": ["용어 정의", "비유적 설명", "기초 개념"],
      "estimated_hours_per_week": 2,
      "order": 1
    }
    // ... 5단계 전체
  ]
}
```

### 3.2 대주제 (Main Topics)

```http
GET /main-topics?category=tech&popular=true&limit=20
```

```json
{
  "items": [
    {
      "id": 1,
      "slug": "ai-ml",
      "name": "인공지능 & 머신러닝",
      "description": "AI, ML, DL, LLM 전반적인 내용",
      "category": "tech",
      "popularity_score": 0.95,
      "total_learners": 15420,
      "avg_completion_rate": 0.73,
      "estimated_learning_time": "4-6주",
      "difficulty_range": ["absolute_beginner", "expert"],
      "subtopic_count": {
        "curated": 12,
        "generated": 156
      }
    }
  ],
  "meta": {
    "total": 25,
    "page": 1,
    "per_page": 20
  }
}
```

### 3.3 소주제 생성 및 조회

**큐레이션 소주제 조회**

```http
GET /sub-topics/curated?main_slug=ai-ml&level=intermediate&limit=10
```

```json
{
  "items": [
    {
      "id": "curated_1",
      "main_topic_id": 1,
      "slug": "transformers-architecture",
      "name": "트랜스포머 아키텍처",
      "description": "Attention 메커니즘과 인코더-디코더 구조",
      "source_type": "curated",
      "quality_score": 0.96,
      "usage_count": 1250,
      "avg_rating": 4.3,
      "learning_outcomes": ["Self-attention 이해", "BERT/GPT 구조 파악"]
    }
  ]
}
```

**개인화 소주제 생성**

```http
POST /sub-topics/generate
```

```json
{
  "main_topic_id": 1,
  "personalization": {
    "interests": ["chatbot", "automation", "nlp"],
    "current_level": "intermediate",
    "learning_goals": "업무 자동화 도구 개발",
    "time_availability": "regular",
    "preferred_style": "practical"
  },
  "options": {
    "max_subtopics": 5,
    "include_prerequisites": true,
    "difficulty_progression": true
  }
}
```

```json
{
  "generation_id": "gen_abc123",
  "status": "processing",
  "estimated_completion": "2024-08-30T15:30:00Z",
  "message": "AI가 당신의 관심사를 분석하고 맞춤 주제를 생성하고 있습니다..."
}
```

**생성된 소주제 조회**

```http
GET /sub-topics/generated/{generation_id}
```

```json
{
  "generation_id": "gen_abc123",
  "status": "completed",
  "items": [
    {
      "id": "generated_456",
      "name": "ChatGPT API 업무 자동화",
      "description": "ChatGPT API를 활용한 반복 업무 자동화 스크립트 개발",
      "estimated_learning_time": "1-2주",
      "prerequisites": ["Python 기초", "API 이해"],
      "practical_projects": ["이메일 자동 분류기", "보고서 생성 봇"]
    }
  ]
}
```

### 3.4 학습 세션 관리

**세션 생성**

```http
POST /sessions
```

```json
{
  "main_topic_id": 1,
  "sub_topic_ids": ["curated_1", "generated_456"],
  "level": "intermediate",
  "personalization": {
    "learning_pace": "regular",
    "preferred_article_length": "medium",
    "include_examples": true
  },
  "options": {
    "max_articles_per_subtopic": 7,
    "enable_adaptive_difficulty": true,
    "include_practice_problems": false
  }
}
```

```json
{
  "session_id": "sess_xyz789",
  "status": "initializing",
  "estimated_total_time": "3-4주",
  "websocket_url": "ws://api.infou.com/sessions/sess_xyz789/ws"
}
```

**세션 상태 조회**

```http
GET /sessions/{session_id}
```

```json
{
  "session_id": "sess_xyz789",
  "status": "ready",
  "created_at": "2024-08-30T14:00:00Z",
  "expires_at": "2024-09-30T14:00:00Z",
  "curriculum": {
    "title": "인공지능 실무 활용 중급",
    "level": "intermediate",
    "total_articles": 14,
    "completed_articles": 0,
    "estimated_completion_time": "3-4주"
  },
  "progress": {
    "current_article_id": "art_001",
    "completion_percentage": 0,
    "time_spent": "0분",
    "last_accessed": null
  },
  "generation_info": {
    "llm_model": "gpt-4",
    "generation_time": "2분 15초",
    "total_tokens_used": 15420
  }
}
```

### 3.5 커리큘럼 및 아티클

**커리큘럼 조회**

```http
GET /sessions/{session_id}/curriculum
```

```json
{
  "session_id": "sess_xyz789",
  "title": "인공지능 실무 활용 중급",
  "level": "intermediate",
  "items": [
    {
      "id": "art_001",
      "order": 1,
      "title": "ChatGPT API 기본 설정",
      "summary": "API 키 발급부터 첫 호출까지",
      "sub_topic": "ChatGPT API 업무 자동화",
      "estimated_read_time": "3-4분",
      "key_concepts": ["API 인증", "기본 파라미터", "에러 처리"],
      "is_generated": true,
      "difficulty_indicators": ["코드 예제 포함", "실습 위주"]
    }
  ]
}
```

**아티클 상세 조회**

```http
GET /articles/{article_id}?level=intermediate
```

```json
{
  "id": "art_001",
  "title": "ChatGPT API 기본 설정",
  "content": "ChatGPT API를 사용하기 위해 먼저 OpenAI 계정을 생성하고...",
  "level": "intermediate",
  "sub_topic_slug": "chatgpt-api-automation",
  "word_count": 487,
  "estimated_read_time": "3-4분",
  "
  "next_article_id": "art_002",
  "previous_article_id": null,

  "metadata": {
    "generated_at": "2024-08-30T14:15:00Z",
    "llm_model": "gpt-4-turbo",
    "generation_prompt": "Write an intermediate-level article...",
    "quality_score": 0.87,
    "human_reviewed": false
  },

  "learning_elements": {
    "key_terms": ["API Key", "Authentication", "Rate Limiting"],
    "code_examples": 2,
    "practical_tips": ["API 키 보안", "요청 최적화"],
    "related_concepts": ["RESTful API", "JSON 응답 처리"]
  },

  "difficulty_variants": {
    "available_levels": ["beginner", "intermediate", "advanced"],
    "current_level": "intermediate"
  }
}
```

**난이도별 아티클 변환**

```http
GET /articles/{article_id}/convert?target_level=beginner
```

- 동일 주제를 다른 난이도로 재생성
- 캐시된 경우 즉시 반환, 없으면 백그라운드 생성

### 3.6 실시간 상태 업데이트

**WebSocket 연결**

```
ws://api.infou.com/sessions/{session_id}/ws
```

**메시지 형태**

```json
{
  "type": "generation_progress",
  "data": {
    "status": "generating_articles",
    "progress": {
      "completed": 3,
      "total": 14,
      "current_task": "ChatGPT 활용 사례 아티클 생성 중...",
      "estimated_remaining": "1분 30초"
    }
  }
}

{
  "type": "generation_complete",
  "data": {
    "session_id": "sess_xyz789",
    "total_articles": 14,
    "generation_time": "2분 45초",
    "ready_to_start": true
  }
}

{
  "type": "error",
  "data": {
    "error_code": "LLM_RATE_LIMIT",
    "message": "LLM API 요청 한도 초과. 잠시 후 다시 시도됩니다.",
    "retry_after": "30초",
    "auto_retry": true
  }
}
```

### 3.7 사용자 피드백 및 분석

**아티클 피드백**

```http
POST /articles/{article_id}/feedback
```

```json
{
  "rating": "like", // "like" | "dislike"
  "feedback_type": ["difficulty", "clarity", "usefulness"],
  "comments": "예제가 더 있으면 좋겠어요",
  "difficulty_perceived": "appropriate", // "too_easy" | "appropriate" | "too_hard"
  "session_id": "sess_xyz789"
}
```

**학습 진행 기록**

```http
POST /sessions/{session_id}/progress
```

```json
{
  "article_id": "art_001",
  "action": "completed", // "started" | "completed" | "bookmarked" | "skipped"
  "time_spent": 180, // seconds
  "scroll_depth": 0.95,
  "engagement_score": 0.87
}
```

---

## 4. 데이터베이스 설계 (ERD v1.0)

### 4.1 기본 주제 구조

```sql
-- 난이도 정의
CREATE TABLE levels (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    target_audience TEXT,
    characteristics TEXT[], -- PostgreSQL 배열
    estimated_hours_per_week INTEGER,
    order_num INTEGER UNIQUE
);

-- 대주제
CREATE TABLE main_topics (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(30),
    popularity_score DECIMAL(3,2) DEFAULT 0.0,
    total_learners INTEGER DEFAULT 0,
    avg_completion_rate DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 큐레이션 소주제
CREATE TABLE curated_sub_topics (
    id SERIAL PRIMARY KEY,
    main_topic_id INTEGER REFERENCES main_topics(id) ON DELETE CASCADE,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    learning_outcomes TEXT[],
    prerequisites TEXT[],
    quality_score DECIMAL(3,2) DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    avg_rating DECIMAL(2,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_main_curated_slug UNIQUE(main_topic_id, slug)
);
```

### 4.2 LLM 생성 관련

```sql
-- LLM 생성 소주제
CREATE TABLE generated_sub_topics (
    id SERIAL PRIMARY KEY,
    generation_batch_id VARCHAR(50) NOT NULL, -- 한 번에 생성된 그룹
    main_topic_id INTEGER REFERENCES main_topics(id),

    -- 기본 정보
    slug VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    learning_outcomes TEXT[],
    prerequisites TEXT[],
    practical_projects TEXT[],

    -- 생성 메타데이터
    generation_prompt TEXT NOT NULL,
    llm_model VARCHAR(50) NOT NULL,
    llm_temperature DECIMAL(2,1),
    generation_params JSONB, -- 기타 LLM 파라미터

    -- 개인화 정보
    personalization_input JSONB, -- 사용자 입력 원본
    target_audience TEXT,
    difficulty_focus VARCHAR(20),

    -- 품질 관리
    quality_score DECIMAL(3,2) DEFAULT 0.0,
    human_reviewed BOOLEAN DEFAULT FALSE,
    review_notes TEXT,
    approval_status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected

    -- 사용 통계
    usage_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,

    -- 메타
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- 개인화 생성의 경우 만료

    CONSTRAINT unique_batch_slug UNIQUE(generation_batch_id, slug)
);

-- 소주제 생성 요청 로그
CREATE TABLE subtopic_generation_requests (
    id SERIAL PRIMARY KEY,
    generation_batch_id VARCHAR(50) UNIQUE NOT NULL,
    main_topic_id INTEGER REFERENCES main_topics(id),
    user_session_id VARCHAR(100), -- 익명 세션 추적

    -- 요청 정보
    personalization_input JSONB NOT NULL,
    generation_options JSONB,

    -- 처리 상태
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,

    -- 결과
    generated_count INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    llm_cost_usd DECIMAL(8,4) DEFAULT 0.0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 학습 세션 관리

```sql
-- 사용자 학습 세션
CREATE TABLE learning_sessions (
    id VARCHAR(50) PRIMARY KEY, -- sess_uuid 형태
    main_topic_id INTEGER REFERENCES main_topics(id),

    -- 선택된 소주제들
    selected_subtopics JSONB NOT NULL, -- [{"type": "curated", "id": 1}, {"type": "generated", "id": 456}]
    target_level VARCHAR(20) REFERENCES levels(code) NOT NULL,

    -- 개인화 설정
    personalization_settings JSONB,
    generation_options JSONB,

    -- 세션 상태
    status VARCHAR(20) DEFAULT 'initializing', -- initializing, generating, ready, active, completed, expired
    curriculum_generated_at TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,

    -- 진행 정보
    total_articles INTEGER DEFAULT 0,
    completed_articles INTEGER DEFAULT 0,
    current_article_id VARCHAR(50),
    last_accessed_at TIMESTAMP,
    total_time_spent INTEGER DEFAULT 0, -- seconds

    -- 생성 메타데이터
    generation_llm_model VARCHAR(50),
    generation_total_tokens INTEGER DEFAULT 0,
    generation_cost_usd DECIMAL(8,4) DEFAULT 0.0,
    generation_duration_seconds INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 동적 생성 아티클
CREATE TABLE generated_articles (
    id VARCHAR(50) PRIMARY KEY, -- sess_uuid_001 형태
    session_id VARCHAR(50) REFERENCES learning_sessions(id) ON DELETE CASCADE,

    -- 아티클 기본 정보
    order_num INTEGER NOT NULL,
    title VARCHAR(300) NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    word_count INTEGER,
    estimated_read_time VARCHAR(20),

    -- 연결 정보
    next_article_id VARCHAR(50),
    previous_article_id VARCHAR(50),

    -- 주제 연결
    sub_topic_type VARCHAR(20) NOT NULL, -- curated, generated
    sub_topic_id INTEGER NOT NULL,
    target_level VARCHAR(20) REFERENCES levels(code) NOT NULL,

    -- 학습 요소
    key_concepts TEXT[],
    key_terms JSONB, -- [{"term": "API", "definition": "..."}]
    code_examples_count INTEGER DEFAULT 0,
    practical_tips TEXT[],
    related_concepts TEXT[],

    -- LLM 생성 메타데이터
    generation_prompt TEXT NOT NULL,
    llm_model VARCHAR(50) NOT NULL,
    llm_temperature DECIMAL(2,1),
    generation_params JSONB,
    generation_tokens_used INTEGER,
    generation_cost_usd DECIMAL(6,4),

    -- 품질 관리
    quality_score DECIMAL(3,2) DEFAULT 0.0,
    human_reviewed BOOLEAN DEFAULT FALSE,
    content_warnings TEXT[], -- ["contains_code", "requires_prerequisites"]

    -- 난이도 변형 지원
    base_article_id VARCHAR(50), -- 다른 난이도에서 변환된 경우
    available_levels VARCHAR(20)[], -- 생성 가능한 난이도들

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_session_order UNIQUE(session_id, order_num),
    CONSTRAINT fk_next_article FOREIGN KEY (next_article_id) REFERENCES generated_articles(id),
    CONSTRAINT fk_previous_article FOREIGN KEY (previous_article_id) REFERENCES generated_articles(id)
);
```

### 4.4 비동기 작업 관리

```sql
-- 백그라운드 생성 작업
CREATE TABLE generation_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL, -- Celery task ID
    session_id VARCHAR(50) REFERENCES learning_sessions(id),

    -- 작업 정보
    task_type VARCHAR(30) NOT NULL, -- curriculum_generation, article_generation, level_conversion
    priority INTEGER DEFAULT 0,

    -- 입력 데이터
    input_data JSONB NOT NULL,

    -- 진행 상태
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    progress_percentage INTEGER DEFAULT 0,
    current_step TEXT,
    estimated_completion_time TIMESTAMP,

    -- 결과
    result_data JSONB,
    error_details JSONB,

    -- 리소스 사용량
    tokens_used INTEGER DEFAULT 0,
    processing_time_seconds INTEGER DEFAULT 0,
    llm_api_calls INTEGER DEFAULT 0,

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- 재시도 관리
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP
);

-- WebSocket 연결 관리
CREATE TABLE websocket_connections (
    id SERIAL PRIMARY KEY,
    connection_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(50) REFERENCES learning_sessions(id),

    -- 연결 정보
    client_ip INET,
    user_agent TEXT,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_ping_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 상태
    is_active BOOLEAN DEFAULT TRUE,
    disconnect_reason VARCHAR(50)
);
```

### 4.5 사용자 피드백 및 분석

```sql
-- 아티클 피드백
CREATE TABLE article_feedback (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(50) REFERENCES generated_articles(id) ON DELETE CASCADE,
    session_id VARCHAR(50) REFERENCES learning_sessions(id),

    -- 피드백 내용
    rating VARCHAR(20) NOT NULL, -- like, dislike
    feedback_types TEXT[], -- difficulty, clarity, usefulness, accuracy
    comments TEXT,
    difficulty_perceived VARCHAR(20), -- too_easy, appropriate, too_hard

    -- 컨텍스트
    user_level_at_time VARCHAR(20),
    time_spent_reading INTEGER, -- seconds
    scroll_depth DECIMAL(3,2), -- 0.0 - 1.0

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 학습 진행 로그
CREATE TABLE learning_progress_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES learning_sessions(id),
    article_id VARCHAR(50) REFERENCES generated_articles(id),

    -- 액션 정보
    action VARCHAR(20) NOT NULL, -- started, completed, bookmarked, skipped, level_switched
    from_level VARCHAR(20),
    to_level VARCHAR(20),

    -- 성능 메트릭
    time_spent_seconds INTEGER DEFAULT 0,
    scroll_depth DECIMAL(3,2),
    engagement_score DECIMAL(3,2), -- 0.0 - 1.0

    -- 컨텍스트
    device_type VARCHAR(20),
    referrer_url TEXT,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 세션 통계 (집계 테이블)
CREATE TABLE session_analytics (
    session_id VARCHAR(50) PRIMARY KEY REFERENCES learning_sessions(id),

    -- 완성도 메트릭
    completion_rate DECIMAL(3,2) DEFAULT 0.0,
    avg_time_per_article INTEGER DEFAULT 0,
    total_engagement_score DECIMAL(3,2) DEFAULT 0.0,

    -- 피드백 메트릭
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    avg_difficulty_rating DECIMAL(2,1) DEFAULT 0.0,

    -- 행동 패턴
    level_switches_count INTEGER DEFAULT 0,
    most_used_level VARCHAR(20),
    preferred_article_length INTEGER, -- words

    -- 업데이트 시간
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.6 성능 최적화 인덱스

```sql
-- 검색 성능 최적화
CREATE INDEX idx_main_topics_category_popularity ON main_topics(category, popularity_score DESC);
CREATE INDEX idx_curated_subtopics_main_usage ON curated_sub_topics(main_topic_id, usage_count DESC);
CREATE INDEX idx_generated_subtopics_batch_status ON generated_sub_topics(generation_batch_id, approval_status);

-- 세션 관련 조회 최적화
CREATE INDEX idx_learning_sessions_status_created ON learning_sessions(status, created_at DESC);
CREATE INDEX idx_generated_articles_session_order ON generated_articles(session_id, order_num);
CREATE INDEX idx_generated_articles_level_quality ON generated_articles(target_level, quality_score DESC);

-- 실시간 조회 최적화
CREATE INDEX idx_generation_tasks_status_priority ON generation_tasks(status, priority DESC, created_at);
CREATE INDEX idx_websocket_connections_session_active ON websocket_connections(session_id) WHERE is_active = TRUE;

-- 분석 쿼리 최적화
CREATE INDEX idx_article_feedback_rating_created ON article_feedback(rating, created_at DESC);
CREATE INDEX idx_progress_logs_session_timestamp ON learning_progress_logs(session_id, timestamp DESC);

-- 파티셔닝 (대용량 데이터 대응)
-- 월별 파티셔닝 예시
CREATE TABLE learning_progress_logs_202408 PARTITION OF learning_progress_logs
FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
```

---

## 5. 비기능 요구사항

### 5.1 성능 목표

**응답 시간**

- 메타데이터 조회 (주제, 난이도): p95 ≤ 100ms
- 소주제 생성 트리거: ≤ 200ms (백그라운드 처리 시작)
- 세션 상태 조회: p95 ≤ 150ms
- 아티클 조회 (캐시 적중): p95 ≤ 200ms
- 아티클 생성 (LLM): p95 ≤ 10초

**처리량**

- 동시 세션 생성: 100 req/min
- 동시 아티클 조회: 1000 req/min
- WebSocket 연결: 500 동시 연결

### 5.2 확장성 및 안정성

**데이터베이스**

- 읽기 전용 복제본 2개 (로드 밸런싱)
- 연결 풀링: pgbouncer (최대 200 커넥션)
- 쿼리 캐싱: Redis (TTL 5-60분)

**비동기 처리**

- Celery 워커 5개 (LLM 생성 전용)
- Redis 큐 (우선순위 큐 지원)
- 재시도 정책: 지수 백오프 (최대 3회)

**캐싱 전략**

```python
# Redis 캐시 키 설계
CACHE_KEYS = {
    "main_topics": "mt:all:v1",  # TTL: 1시간
    "subtopic_curated": "st:c:{main_id}:{level}:v1",  # TTL: 30분
    "article_content": "art:{article_id}:{level}:v1",  # TTL: 24시간
    "session_status": "sess:{session_id}:status:v1",  # TTL: 5분
    "generation_progress": "gen:{task_id}:progress:v1"  # TTL: 1시간
}
```

### 5.3 LLM 통합 및 비용 최적화

**멀티 프로바이더 지원**

```python
LLM_PROVIDERS = {
    "openai_gpt4": {
        "model": "gpt-4-turbo",
        "cost_per_token": 0.00003,
        "rate_limit": "10000/min",
        "use_cases": ["high_quality_generation", "complex_topics"]
    },
    "anthropic_claude": {
        "model": "claude-3.5-sonnet",
        "cost_per_token": 0.000015,
        "rate_limit": "5000/min",
        "use_cases": ["balanced_cost_quality", "creative_content"]
    },
    "local_llm": {
        "model": "llama-3-70b",
        "cost_per_token": 0.000001,
        "rate_limit": "1000/min",
        "use_cases": ["cost_optimization", "privacy_sensitive"]
    }
}
```

**비용 관리**

- 일일 LLM 사용량 모니터링 및 예산 제한
- 토큰 사용량 예측 및 알림
- 캐시 우선 정책 (동일 주제+난이도 재사용)

### 5.4 보안 및 개인정보

**API 보안**

- API 키 기반 인증 (세션별 임시 토큰)
- Rate limiting: IP별 100 req/min
- CORS 정책: 허용된 도메인만
- SQL Injection 방지: SQLAlchemy ORM 사용

**데이터 보안**

- 개인화 입력 데이터 암호화 (AES-256)
- 민감 정보 자동 만료 (90일)
- 로그 개인정보 마스킹

---

## 6. 배포 및 모니터링

### 6.1 배포 아키텍처

**컨테이너 구성**

```yaml
services:
  api:
    image: infou-api:v1.0
    replicas: 3
    resources:
      memory: 2GB
      cpu: 1.0

  worker:
    image: infou-worker:v1.0
    replicas: 5
    resources:
      memory: 4GB # LLM 처리용
      cpu: 2.0

  websocket:
    image: infou-ws:v1.0
    replicas: 2
    resources:
      memory: 1GB
      cpu: 0.5
```

**로드 밸런싱**

- Nginx: API 엔드포인트 (라운드 로빈)
- HAProxy: WebSocket (sticky session)

### 6.2 모니터링 및 알림

**핵심 메트릭**

```python
METRICS_TO_TRACK = {
    "api_response_time": "histogram",
    "llm_generation_time": "histogram",
    "active_sessions": "gauge",
    "generation_success_rate": "counter",
    "cache_hit_rate": "gauge",
    "database_connection_pool": "gauge",
    "websocket_connections": "gauge",
    "daily_llm_cost": "counter"
}
```

**알림 규칙**

- API 응답시간 > 1초 (5분 연속)
- LLM 생성 실패율 > 5% (10분 윈도우)
- 데이터베이스 커넥션 풀 > 80%
- 일일 LLM 비용 > $100

### 6.3 로그 및 디버깅

**구조화된 로깅**

```python
LOG_STRUCTURE = {
    "timestamp": "2024-08-30T14:30:00Z",
    "level": "INFO",
    "service": "api",
    "endpoint": "/sessions",
    "session_id": "sess_xyz789",
    "user_id": "anon_abc123",
    "duration_ms": 245,
    "llm_provider": "openai",
    "tokens_used": 1500,
    "cache_hit": false,
    "error": null
}
```

---

## 7. 테스트 전략

### 7.1 단위 테스트

- LLM 프롬프트 생성 로직
- 난이도 전환 알고리즘
- 캐싱 계층 동작
- 데이터베이스 모델 검증

### 7.2 통합 테스트

- 전체 생성 워크플로우 (주제 선택 → 아티클 완성)
- WebSocket 실시간 업데이트
- LLM API 오류 처리
- 세션 만료 및 복구

### 7.3 성능 테스트

- 동시 세션 생성 부하 (100/min)
- LLM API 레이트 리미트 대응
- 데이터베이스 커넥션 풀 최대치
- 캐시 무효화 시나리오

### 7.4 품질 게이트

- LLM 생성 아티클 품질 검증 (길이, 난이도 적합성)
- 개인화 정확도 측정
- 사용자 만족도 피드백 분석
- 토큰 사용 효율성 모니터링

---

✅ **백엔드 성공 지표**

- **생성 성공률**: 95% 이상
- **평균 생성 시간**: 커리큘럼 3분, 아티클 10초 이내
- **API 가용성**: 99.9% (월간)
- **비용 효율성**: 사용자당 평균 LLM 비용 $0.50 이하
- **사용자 만족도**: 생성 품질 평점 4.0/5.0 이상
