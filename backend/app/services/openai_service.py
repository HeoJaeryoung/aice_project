import json
import re
from typing import List

from openai import OpenAI

from app.core.config import settings
from app.schemas import ClaudeQuestionSchema


SYSTEM_PROMPT = """당신은 AICE Associate 자격증 전문 출제위원입니다.
실제 시험과 동일한 스타일로 4지선다 객관식 문제를 출제합니다.

출제 기준:
1. KT AI 플랫폼 맥락에 맞는 실무형 문제
2. 명확한 정답과 상세한 해설 제공
3. 오답 선택지도 그럴듯하게 작성
4. 난이도에 맞는 문제 구성

난이도 기준:
- easy: 기본 개념 확인, 단순 암기형
- medium: 개념 이해 및 적용, 분석형
- hard: 복합 개념, 실무 응용, 추론형"""


def get_user_prompt(topic: str, difficulty: str, count: int) -> str:
    return f"""다음 조건으로 AICE Associate 문제 {count}개를 생성하세요.

주제: {topic}
난이도: {difficulty}
문제 수: {count}개

반드시 다음 JSON 배열 형식으로만 응답하세요:
[
  {{
    "question_text": "문제 내용",
    "option_a": "선택지 A",
    "option_b": "선택지 B",
    "option_c": "선택지 C",
    "option_d": "선택지 D",
    "correct_answer": "a",
    "explanation": "상세한 해설",
    "difficulty": "{difficulty}"
  }}
]

주의사항:
- 반드시 유효한 JSON 배열만 응답하세요
- correct_answer는 반드시 a, b, c, d 중 하나의 소문자여야 합니다
- 각 문제는 서로 다른 내용이어야 합니다
- 해설은 왜 정답이 맞고 오답이 틀린지 설명해야 합니다"""


def parse_gpt_response(content: str) -> List[dict]:
    """Parse GPT API response and extract questions."""
    # Remove markdown code blocks if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    # Try to find JSON array in content
    json_match = re.search(r'\[[\s\S]*\]', content)
    if json_match:
        content = json_match.group()

    questions = json.loads(content.strip())
    return questions


def validate_question(q: dict) -> bool:
    """Validate question has all required fields."""
    required = [
        "question_text", "option_a", "option_b",
        "option_c", "option_d", "correct_answer", "explanation"
    ]

    for field in required:
        if field not in q or not q[field]:
            return False

    if q["correct_answer"].lower() not in ["a", "b", "c", "d"]:
        return False

    return True


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_questions(
        self,
        topic_name: str,
        difficulty: str,
        count: int,
    ) -> List[ClaudeQuestionSchema]:
        """Generate questions using OpenAI GPT API."""
        user_prompt = get_user_prompt(topic_name, difficulty, count)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                max_tokens=4096,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            raw_questions = parse_gpt_response(content)

            validated_questions = []
            for q in raw_questions:
                if validate_question(q):
                    # Normalize correct_answer to lowercase
                    q["correct_answer"] = q["correct_answer"].lower()
                    # Set difficulty if not present
                    if "difficulty" not in q:
                        q["difficulty"] = difficulty
                    validated_questions.append(ClaudeQuestionSchema(**q))

            return validated_questions

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse GPT response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"OpenAI API error: {e}")


# Singleton instance
openai_service = OpenAIService()
