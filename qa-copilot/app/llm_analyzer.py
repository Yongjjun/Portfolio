import json
import time
from pathlib import Path

from google import genai
from evaluate_rules import TEST_DATASET


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "gemini-3.5-flash"

BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_FILE = BASE_DIR / "data" / "llm_results.json"

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


# ============================================================
# Result File
# ============================================================

def load_results():
    """기존 Gemini 분석 결과를 불러온다."""

    if not RESULT_FILE.exists():
        return {}

    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError:
        print("⚠️ 기존 결과 파일의 JSON 형식이 올바르지 않습니다.")
        return {}


def save_results(results):
    """Gemini 분석 결과를 JSON 파일에 저장한다."""

    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# Gemini Analysis
# ============================================================

def analyze_requirement(requirement: str):

    prompt = f"""
너는 5년차 소프트웨어 QA 엔지니어다.

아래 요구사항을 QA 관점에서 분석하고,
적용 가능한 QA Rule을 선택하라.

사용 가능한 Rule은 다음 10개로 제한한다.

{RULES}

각 Rule에 대해 다음 정보를 반환하라.

- rule: Rule 이름
- reason: 해당 Rule이 필요한 이유
- confidence: 0~1 사이의 신뢰도

주의사항:

1. 요구사항에 직접적으로 관련된 Rule만 선택하라.
2. 모든 Rule을 무조건 선택하지 마라.
3. QA 관점에서 실제 테스트에 의미가 있는 Rule만 선택하라.
4. 하나의 요구사항에 여러 Rule이 적용될 수 있다.
5. 반드시 아래 JSON 배열 형식으로만 응답하라.
6. Markdown 코드블록은 사용하지 마라.

응답 형식:

[
  {{
    "rule": "Business Rule",
    "reason": "해당 Rule이 필요한 이유",
    "confidence": 0.95
  }}
]

요구사항:
{requirement}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text


# ============================================================
# Single Test Case
# ============================================================

def process_case(case, results):

    case_id = case["id"]

    # 이미 성공적으로 분석한 TC라면 API 호출하지 않음
    if case_id in results and results[case_id].get("status") == "success":

        print(f"[{case_id}] SKIP - 이미 분석된 결과가 존재합니다.")

        return


    print(f"\n[{case_id}]")
    print(f"Requirement : {case['requirement']}")
    print(f"Expected    : {case['expected']}")

    try:

        raw_result = analyze_requirement(
            case["requirement"]
        )

        rules = json.loads(raw_result)

        actual = [
            item["rule"]
            for item in rules
        ]

        results[case_id] = {
            "requirement": case["requirement"],
            "expected": case["expected"],
            "rules": rules,
            "actual": actual,
            "status": "success",
        }

        save_results(results)

        print(f"Gemini      : {actual}")
        print("Status      : SUCCESS")

    except Exception as e:

        error_message = str(e)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

            status = "rate_limit"

        else:

            status = "error"


        results[case_id] = {
            "requirement": case["requirement"],
            "expected": case["expected"],
            "rules": [],
            "actual": [],
            "status": status,
            "error": error_message,
        }

        save_results(results)

        print(f"Gemini      : ERROR")
        print(f"Status      : {status}")
        print(f"Error       : {error_message}")


# ============================================================
# Evaluation
# ============================================================

def evaluate_llm():

    print("=" * 80)
    print("🤖 Gemini QA Rule Analysis")
    print("=" * 80)

    results = load_results()

    print(f"\nResult File : {RESULT_FILE}")
    print(f"Saved Cases : {len(results)}")

    for case in TEST_DATASET:

        process_case(case, results)

        # 무료 티어 Rate Limit 대응
        # API 호출 사이에 잠시 대기
        time.sleep(2)

    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    evaluate_llm()