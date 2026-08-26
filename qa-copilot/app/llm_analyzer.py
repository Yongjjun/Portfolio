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


# ============================================================
# Retry Configuration
# ============================================================

# 일시적인 Gemini API 오류 발생 시 재시도 횟수
MAX_RETRIES = 3

# 첫 번째 재시도까지 대기 시간
# 이후 2초 → 4초 → 8초로 증가
INITIAL_RETRY_DELAY = 2


# ============================================================
# QA Rule Definition
# ============================================================
#
# RuleEngine.md의 기준을 코드로 정의한다.
#
# Gemini는 일반적인 QA 지식보다
# 아래에 정의된 Selection / Exclusion Criteria를
# 우선하여 판단한다.
#

RULE_DEFINITIONS = {

    "Validation": {
        "trigger": "사용자 입력 필드가 존재",
        "selection": (
            "입력값의 형식 또는 필수 여부 자체가 "
            "요구사항의 핵심인 경우"
        ),
        "exclusion": (
            "단순히 숫자나 문자 값이 언급된 것만으로 "
            "선택하지 않음"
        ),
    },

    "Boundary Value": {
        "trigger": "최소/최대/범위 제한 존재",
        "selection": (
            "명시적인 최소값, 최대값 또는 범위의 "
            "경계값 검증이 핵심인 경우"
        ),
        "exclusion": (
            "단순한 조건이나 제한이라는 이유만으로 "
            "선택하지 않음"
        ),
    },

    "Equivalence Partition": {
        "trigger": "유효/무효 그룹 구분 가능",
        "selection": (
            "입력값 그룹을 나누어 대표값 테스트가 "
            "필요한 경우"
        ),
        "exclusion": (
            "단순히 정상/비정상 입력이 가능하다는 "
            "이유만으로 선택하지 않음"
        ),
    },

    "Negative Test": {
        "trigger": "예외/잘못된 입력 가능",
        "selection": (
            "잘못된 입력이나 실패 상황에 대한 "
            "시스템 반응이 요구사항에 포함된 경우"
        ),
        "exclusion": (
            "단순히 제한이나 불가 조건이 있다는 "
            "이유만으로 선택하지 않음"
        ),
    },

    "Business Rule": {
        "trigger": "정책/업무 규칙 존재",
        "selection": (
            "서비스 정책이나 업무 조건 자체를 "
            "검증하는 것이 핵심인 경우"
        ),
        "exclusion": (
            "단순한 입력 검증이나 UI 동작만으로 "
            "선택하지 않음"
        ),
    },

    "State Transition": {
        "trigger": "상태 변경 존재",
        "selection": (
            "명확한 상태 변화 또는 상태 간 이동을 "
            "검증해야 하는 경우"
        ),
        "exclusion": (
            "단순히 데이터가 변경되었다는 이유만으로 "
            "선택하지 않음"
        ),
    },

    "Regression": {
        "trigger": "기존 기능 변경",
        "selection": (
            "기존 기능에 대한 영향 또는 회귀 검증이 "
            "요구사항에 명시되거나 명확한 경우"
        ),
        "exclusion": (
            "단순히 수정이나 변경이라는 단어만으로 "
            "선택하지 않음"
        ),
    },

    "Platform": {
        "trigger": "여러 플랫폼 존재",
        "selection": (
            "플랫폼별 동작 차이 또는 동일성 검증이 "
            "요구사항의 핵심인 경우"
        ),
        "exclusion": (
            "플랫폼명이 언급되었더라도 플랫폼 차이가 "
            "검증 대상이 아니면 선택하지 않음"
        ),
    },

    "Accessibility": {
        "trigger": "접근성 요구 존재",
        "selection": (
            "접근성 기능 또는 사용성 보장이 "
            "명시된 경우"
        ),
        "exclusion": (
            "화면 크기나 다양한 환경만으로 "
            "접근성을 선택하지 않음"
        ),
    },

    "Security": {
        "trigger": "인증/권한/민감정보",
        "selection": (
            "인증, 권한 또는 개인정보 보호 자체가 "
            "검증 대상인 경우"
        ),
        "exclusion": (
            "로그인이나 개인정보라는 단어만으로 "
            "보안 Rule을 자동 선택하지 않음"
        ),
    },

    "No Applicable Rule": {
        "trigger": "정의된 Rule과 직접적인 연관이 없음",
        "selection": (
            "현재 정의된 Rule로 요구사항의 핵심 "
            "검증 목적을 표현할 수 없는 경우"
        ),
        "exclusion": (
            "기존 Rule이 직접적으로 적용 가능한 "
            "경우에는 선택하지 않음"
        ),
    },
}


# 사용 가능한 Rule 목록
RULES = list(RULE_DEFINITIONS.keys())


# ============================================================
# Prompt Builder
# ============================================================

def build_rule_definition_prompt():
    """
    Rule Definition을 Gemini Prompt에 전달할 문자열로 변환한다.
    """

    lines = []

    for rule, definition in RULE_DEFINITIONS.items():

        lines.append(
            f"""
### {rule}
- Trigger: {definition["trigger"]}
- Selection Criteria: {definition["selection"]}
- Exclusion Criteria: {definition["exclusion"]}
""".strip()
        )

    return "\n\n".join(lines)


def build_selection_principle_prompt():
    """
    Rule Selection Principle을 Gemini Prompt에 전달한다.
    """

    return """
1. 요구사항의 핵심 검증 목적을 기준으로 Rule을 선택한다.
2. 단순히 적용 가능한 테스트 기법이라는 이유만으로 Rule을 추가하지 않는다.
3. 하나의 요구사항에 여러 Rule이 명확하게 필요한 경우 복수 Rule을 선택한다.
4. 요구사항에 직접적인 근거가 없는 Rule은 선택하지 않는다.
5. 다른 Rule과 연관될 수 있다는 이유만으로 Validation이나 Negative Test 등을 자동으로 추가하지 않는다.
6. 수치나 범위가 명시된 경우 Boundary Value를 고려한다.
7. 정책이나 업무 조건이 핵심인 경우 Business Rule을 고려한다.
8. 상태 간 이동이 핵심인 경우 State Transition을 고려한다.
9. 여러 플랫폼 간 동작 차이 또는 동일성이 핵심인 경우 Platform을 선택한다.
10. 인증, 권한 또는 개인정보 보호가 핵심인 경우 Security를 선택한다.
11. 현재 정의된 Rule 중 요구사항의 핵심 검증 목적을 직접적으로 표현할 수 있는 Rule이 없는 경우 No Applicable Rule을 선택한다.
""".strip()


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

        print(
            "⚠️ 기존 결과 파일의 JSON 형식이 올바르지 않습니다."
        )

        return {}


def save_results(results):
    """Gemini 분석 결과를 JSON 파일에 저장한다."""

    RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(RESULT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# Gemini API Retry
# ============================================================

def generate_content_with_retry(prompt: str):
    """
    Gemini API 호출 시 일시적인 429/503 오류가 발생하면
    Exponential Backoff 방식으로 재시도한다.

    Retry 대상:
    - 429
    - RESOURCE_EXHAUSTED
    - 503
    - UNAVAILABLE
    """

    for attempt in range(MAX_RETRIES + 1):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            return response

        except Exception as e:

            error_message = str(e)

            is_retryable = (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "503" in error_message
                or "UNAVAILABLE" in error_message
            )

            # Retry 대상이 아닌 오류
            if not is_retryable:
                raise

            # 마지막 시도였다면 오류 발생
            if attempt >= MAX_RETRIES:
                raise

            delay = INITIAL_RETRY_DELAY * (2 ** attempt)

            print(
                f"⚠️ Gemini API 일시적 오류 발생 "
                f"(attempt {attempt + 1}/{MAX_RETRIES + 1})"
            )

            print(
                f"   Error: {error_message}"
            )

            print(
                f"   {delay}초 후 재시도합니다..."
            )

            time.sleep(delay)


# ============================================================
# Gemini Analysis
# ============================================================

def analyze_requirement(requirement: str):
    """
    요구사항을 Gemini에 전달하고
    QA Rule 분석 결과를 반환한다.
    """

    rule_definitions = build_rule_definition_prompt()
    selection_principles = build_selection_principle_prompt()

    prompt = f"""
너는 소프트웨어 QA 엔지니어다.

아래 요구사항을 QA 관점에서 분석하고,
사전에 정의된 QA Rule 중 요구사항의 핵심 검증 목적에
직접적으로 해당하는 Rule만 선택하라.

일반적인 QA 관행보다 아래에 정의된 Rule Definition을
우선하여 판단해야 한다.


============================================================
QA RULE DEFINITIONS
============================================================

{rule_definitions}


============================================================
RULE SELECTION PRINCIPLE
============================================================

{selection_principles}


============================================================
IMPORTANT RULES
============================================================

- Rule의 Trigger만 보고 선택하지 마라.
- 반드시 Selection Criteria와 Exclusion Criteria를 함께 고려하라.
- 요구사항에 명시되지 않은 정보를 추론하여 Rule을 추가하지 마라.
- 일반적인 QA 지식보다 위에서 정의한 Rule 기준을 우선한다.
- 가장 많은 Rule을 선택하는 것이 좋은 결과가 아니다.
- 직접적인 근거가 있는 Rule만 선택한다.
- 하나의 요구사항에 여러 Rule이 명확하게 필요한 경우 복수 Rule을 선택할 수 있다.
- 여러 Rule을 선택할 수 있더라도 불필요한 Rule은 추가하지 않는다.
- 현재 정의된 Rule 중 적절한 Rule이 하나도 없다면 반드시
  "No Applicable Rule"을 선택한다.
- "No Applicable Rule"과 다른 Rule을 동시에 선택하지 않는다.
- 사용 가능한 Rule 목록에 없는 Rule은 절대 생성하지 않는다.


============================================================
AVAILABLE RULES
============================================================

{RULES}


============================================================
OUTPUT FORMAT
============================================================

반드시 아래 JSON 배열 형식으로만 응답하라.

Markdown 코드블록을 사용하지 마라.

[
  {{
    "rule": "Business Rule",
    "reason": "요구사항에서 정책 조건 자체를 검증하는 것이 핵심이므로 선택",
    "confidence": 0.95
  }}
]

각 Rule의 confidence는 0~1 사이의 숫자로 작성한다.


============================================================
REQUIREMENT
============================================================

{requirement}
"""

    response = generate_content_with_retry(prompt)

    return response.text


# ============================================================
# Result Validation
# ============================================================

def validate_rules(rules):
    """
    Gemini가 반환한 Rule이 사전에 정의된 Rule인지 검증한다.
    """

    if not isinstance(rules, list):

        raise ValueError(
            "LLM 응답이 JSON 배열 형식이 아닙니다."
        )

    for item in rules:

        if not isinstance(item, dict):

            raise ValueError(
                "Rule 결과 항목이 객체 형식이 아닙니다."
            )

        rule = item.get("rule")

        if rule not in RULES:

            raise ValueError(
                f"정의되지 않은 Rule이 반환되었습니다: {rule}"
            )

        if "reason" not in item:

            raise ValueError(
                f"{rule} Rule에 reason이 없습니다."
            )

        if "confidence" not in item:

            raise ValueError(
                f"{rule} Rule에 confidence가 없습니다."
            )

        confidence = item["confidence"]

        if not isinstance(
            confidence,
            (int, float),
        ):

            raise ValueError(
                f"{rule} confidence가 숫자가 아닙니다."
            )

        if not 0 <= confidence <= 1:

            raise ValueError(
                f"{rule} confidence가 0~1 범위를 벗어났습니다."
            )

    # No Applicable Rule은 다른 Rule과 동시에 선택할 수 없음

    selected_rules = [
        item["rule"]
        for item in rules
    ]

    if (
        "No Applicable Rule" in selected_rules
        and len(selected_rules) > 1
    ):

        raise ValueError(
            "No Applicable Rule은 다른 Rule과 "
            "동시에 선택할 수 없습니다."
        )

    return True


# ============================================================
# Single Test Case
# ============================================================

def process_case(case, results):

    case_id = case["id"]

    # 이미 성공적으로 분석한 TC라면 API 호출하지 않음

    if (
        case_id in results
        and results[case_id].get("status") == "success"
    ):

        print(
            f"[{case_id}] "
            f"SKIP - 이미 분석된 결과가 존재합니다."
        )

        return

    print(f"\n[{case_id}]")

    print(
        f"Requirement : "
        f"{case['requirement']}"
    )

    print(
        f"Expected    : "
        f"{case['expected']}"
    )

    try:

        raw_result = analyze_requirement(
            case["requirement"]
        )

        # JSON 응답 파싱

        rules = json.loads(
            raw_result
        )

        # LLM 결과 검증

        validate_rules(rules)

        actual = [
            item["rule"]
            for item in rules
        ]

        results[case_id] = {

            "requirement":
                case["requirement"],

            "expected":
                case["expected"],

            "rules":
                rules,

            "actual":
                actual,

            "status":
                "success",
        }

        save_results(results)

        print(
            f"Gemini      : {actual}"
        )

        print(
            "Status      : SUCCESS"
        )

    except Exception as e:

        error_message = str(e)

        # Rate Limit

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
        ):

            status = "rate_limit"

        # Gemini 서버 일시적 장애

        elif (
            "503" in error_message
            or "UNAVAILABLE" in error_message
        ):

            status = "service_unavailable"

        # 그 외 오류

        else:

            status = "error"

        results[case_id] = {

            "requirement":
                case["requirement"],

            "expected":
                case["expected"],

            "rules":
                [],

            "actual":
                [],

            "status":
                status,

            "error":
                error_message,
        }

        save_results(results)

        print(
            "Gemini      : ERROR"
        )

        print(
            f"Status      : {status}"
        )

        print(
            f"Error       : {error_message}"
        )


# ============================================================
# Evaluation
# ============================================================

def evaluate_llm():

    print("=" * 80)

    print(
        "🤖 Gemini QA Rule Analysis"
    )

    print("=" * 80)

    results = load_results()

    print(
        f"\nResult File : "
        f"{RESULT_FILE}"
    )

    print(
        f"Saved Cases : "
        f"{len(results)}"
    )

    for case in TEST_DATASET:

        process_case(
            case,
            results,
        )

        # TC 간 API 호출 간격
        # 무료 티어 Rate Limit 대응

        time.sleep(2)

    print(
        "\n" + "=" * 80
    )

    print(
        "Analysis Complete"
    )

    print(
        "=" * 80
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    evaluate_llm()