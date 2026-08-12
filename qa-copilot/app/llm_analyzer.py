
import json
from google import genai

from evaluate_rules import TEST_DATASET

client = genai.Client()

RULES = [
    "Validation",
    "Boundary Value",
    "Equivalence Partition",
    "Negative Test",
    "Business Rule",
    "State Transition",
    "Regression",
    "Platform",
    "Accessibility",
    "Security",
]


def analyze_requirement(requirement: str):
    prompt = f"""
너는 5년차 소프트웨어 QA 엔지니어다.

아래 요구사항을 QA 관점에서 분석하라.

사용 가능한 QA Rule은 아래 10개로 제한한다.
{RULES}

반드시 아래 JSON 배열 형식으로만 응답하라.

[
  {{
    "rule": "Business Rule",
    "reason": "...",
    "confidence": 0.95
  }}
]

요구사항:
{requirement}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return json.loads(response.text)


def evaluate_llm():
    print("=" * 80)
    print("🤖 Gemini QA Rule Analysis")
    print("=" * 80)

    for case in TEST_DATASET:
        print(f"\n[{case['id']}]")
        print(f"Requirement : {case['requirement']}")
        print(f"Expected    : {case['expected']}")

        try:
            result = analyze_requirement(case["requirement"])

            result = analyze_requirement(case["requirement"])
            actual = [r["rule"] for r in result]

            print(f"Gemini      : {actual}")

        except Exception as e:
            print("Gemini      : ERROR")
            print(e)

        print("-" * 80)


if __name__ == "__main__":
    evaluate_llm()