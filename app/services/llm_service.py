import json
import os
from typing import List, Dict, Optional
from google import genai
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        # Set environment variable for API key
        if settings.gemini_api_key:
            os.environ['GEMINI_API_KEY'] = settings.gemini_api_key
        
        self.client = genai.Client()
        self.model_name = "gemini-1.5-flash"
    
    async def generate_sub_topics(
        self,
        main_topic_title: str,
        main_topic_description: Optional[str] = None,
        personalization_data: Optional[Dict] = None,
        count: int = 10
    ) -> Dict:
        """LLM을 통해 소주제들을 생성합니다."""
        
        try:
            full_prompt = self._get_system_prompt() + "\n\n" + self._build_generation_prompt(
                main_topic_title, 
                main_topic_description, 
                personalization_data, 
                count
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            
            # 응답 파싱
            content = response.text
            
            # 토큰 사용량 계산
            tokens_used = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                if hasattr(response.usage_metadata, 'total_token_count'):
                    tokens_used = response.usage_metadata.total_token_count
                else:
                    # 다른 속성들로 계산 시도
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                    tokens_used = input_tokens + output_tokens
            
            # JSON 파싱 시도 (마크다운 코드 블록 처리 포함)
            json_content = self._extract_json_from_markdown(content)
            
            try:
                result = json.loads(json_content)
                print(f"✅ JSON 파싱 성공: {len(result.get('sub_topics', []))}개 소주제")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                print(f"원본 응답 길이: {len(content)}")
                print(f"추출된 JSON 길이: {len(json_content)}")
                result = {"sub_topics": []}
            
            return {
                "sub_topics": result.get("sub_topics", []),
                "tokens_used": tokens_used,
                "model_used": self.model_name,
                "quality_score": self._calculate_quality_score(result.get("sub_topics", []))
            }
            
        except Exception as e:
            logger.error(f"LLM 소주제 생성 실패: {str(e)}")
            raise Exception(f"소주제 생성 중 오류가 발생했습니다: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트를 반환합니다."""
        return """당신은 교육 전문가입니다. 주어진 대주제에 대해 학습자가 체계적으로 학습할 수 있는 소주제들을 생성해주세요.

**반드시 순수한 JSON 형식으로만 응답하세요. 마크다운이나 다른 텍스트는 포함하지 마세요.**

JSON 형식:
{
  "sub_topics": [
    {
      "title": "소주제 제목",
      "description": "간단한 설명"
    }
  ]
}

규칙:
1. 소주제는 논리적 순서로 배열 (기초 → 심화)
2. title과 description만 포함
3. 순수 JSON만 응답 (```나 다른 텍스트 금지)"""
    
    def _build_generation_prompt(
        self, 
        main_topic_title: str, 
        main_topic_description: Optional[str] = None,
        personalization_data: Optional[Dict] = None,
        count: int = 10
    ) -> str:
        """생성 프롬프트를 구성합니다."""
        
        prompt = f"대주제: {main_topic_title}\n"
        
        if main_topic_description:
            prompt += f"대주제 설명: {main_topic_description}\n"
        
        if personalization_data:
            if personalization_data.get("learning_level"):
                prompt += f"학습자 수준: {personalization_data['learning_level']}\n"
            if personalization_data.get("learning_goals"):
                prompt += f"학습 목표: {', '.join(personalization_data['learning_goals'])}\n"
            if personalization_data.get("preferred_difficulty"):
                prompt += f"선호 난이도: {personalization_data['preferred_difficulty']}\n"
        
        prompt += f"\n위 대주제에 대해 {count}개의 소주제를 생성해주세요."
        
        return prompt
    
    def _extract_from_text(self, content: str) -> Dict:
        """텍스트에서 소주제 정보를 추출합니다."""
        # 간단한 파싱 로직 (실제로는 더 정교한 파싱이 필요할 수 있음)
        lines = content.split('\n')
        sub_topics = []
        
        current_topic = None
        for line in lines:
            line = line.strip()
            if line.startswith('제목:') or line.startswith('title:'):
                if current_topic:
                    sub_topics.append(current_topic)
                current_topic = {
                    "title": line.split(':', 1)[1].strip(),
                    "description": "",
                    "keywords": [],
                    "learning_objectives": [],
                    "prerequisites": [],
                    "estimated_duration_minutes": 30,
                    "difficulty_score": 5
                }
            elif current_topic and (line.startswith('설명:') or line.startswith('description:')):
                current_topic["description"] = line.split(':', 1)[1].strip()
        
        if current_topic:
            sub_topics.append(current_topic)
        
        return {"sub_topics": sub_topics}
    
    def _extract_json_from_markdown(self, content: str) -> str:
        """마크다운 코드 블록에서 JSON 추출"""
        import re
        
        # ```json과 ``` 사이의 내용 추출
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # ```와 ``` 사이의 내용 추출 (json 태그 없이)
        code_pattern = r'```\s*(.*?)\s*```'
        match = re.search(code_pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # 코드 블록이 없으면 원본 반환
        return content.strip()
    
    def _calculate_quality_score(self, sub_topics: List[Dict]) -> float:
        """생성된 소주제들의 품질 점수를 계산합니다."""
        if not sub_topics:
            return 0.0
        
        score = 0.0
        for topic in sub_topics:
            # 각 필드가 적절히 채워져 있는지 확인
            if topic.get("title") and len(topic["title"]) > 5:
                score += 1
            if topic.get("description") and len(topic["description"]) > 10:
                score += 1
            if topic.get("keywords") and len(topic["keywords"]) > 0:
                score += 1
            if topic.get("learning_objectives") and len(topic["learning_objectives"]) > 0:
                score += 1
        
        # 평균 점수를 0-10 범위로 정규화
        max_possible_score = len(sub_topics) * 4
        if max_possible_score > 0:
            normalized_score = (score / max_possible_score) * 10
            return round(normalized_score, 2)
        
        return 0.0


# 싱글톤 인스턴스
llm_service = LLMService()