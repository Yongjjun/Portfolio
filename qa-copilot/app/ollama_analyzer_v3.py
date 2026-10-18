import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from evaluate_rules import TEST_DATASET


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_FILE = (
    BASE_DIR
    / "data"
    / "ollama_qwen3_1.7b_v3_results.json"
)


# ============================================================
# Compact Rule Definitions
# ============================================================

RULE_DEFINITIONS = {
    "Validation":
        "입력값의 형식 또는 필수 여부 자체를 검증하는 경우. "
        "예: 이메일 형식, 필수 입력 여부.",

    "Boundary Value":
        "최소값, 최대값, 이상, 이하, 미만, 초과, 범위처럼 "
        "명시적인 경계 조건을 검증하는 경우.",

    "Equivalence Partition":
        "입력값을 유효/무효 또는 대표 그룹으로 나누어 검증하는 경우.",

    "Negative Test":
        "잘못된 입력이나 실패 상황에 대한 시스템 반응을 검증하는 경우. "
        "오류 메시지, 진행 제한 등 실패 시 동작이 명시된 경우 고려.",

    "Business Rule":
        "서비스 정책 또는 업무 조건 자체를 검증하는 경우.",

    "State Transition":
        "명확한 상태 변화 또는 상태 간 이동을 검증하는 경우.",

    "Regression":
        "기존 기능 변경에 따른 영향이나 회귀 검증이 명시된 경우.",

    "Platform":
        "Web, Android, iOS 등 플랫폼 간 차이 또는 동일성을 검증하는 경우.",

    "Accessibility":
        "접근성 기능 또는 사용성 보장이 명시된 경우.",

    "Security":
        "인증, 권한 또는 개인정보 보호 자체를 검증하는 경우.",

    "No Applicable Rule":
        "현재 정의된 Rule 중 요구사항의 핵심 검증 목적에 "
        "직접 해당하는 Rule이 없는 경우.",
}


RULES = list(RULE_DEFINITIONS.keys())


# ============================================================
# Prompt Builder
# ============================================================

def build_rule_prompt():

    lines = []

    for rule, description in RULE_DEFINITIONS.items():
        lines.append(
            f"- {rule}: {description}"
        )

    return "\n".join(lines)


def build_prompt(requirement: str):

    rule_text = build_rule_prompt()

    return f"""
/no_think

너는 소프트웨어 QA 엔지니어다.

아래 요구사항을 분석하여
정의된 QA Rule 중 핵심 검증 목적에 직접 해당하는 Rule을 모두 선택하라.

QA Rule:
{rule_text}

선택 원칙:
1. 요구사항의 핵심 검증 목적에 직접 해당하는 Rule만 선택한다.
2. 요구사항에 없는 내용을 임의로 추론해서 Rule을 추가하지 않는다.
3. 서로 다른 검증 목적이 여러 개 명시되어 있으면 각각 독립적으로 검토한다.
4. 하나의 Rule을 선택했다고 분석을 종료하지 않는다.

5. 입력 형식 또는 필수 여부가 핵심이면 Validation을 고려한다.

6. 최소값, 최대값, 이상, 이하, 미만, 초과, 범위가 명시되어 있으면
   Boundary Value를 별도의 검증 관점으로 반드시 검토한다.

7. Boundary Value는 Validation 또는 Business Rule과 동시에 선택될 수 있다.

8. 잘못된 입력, 실패 조건, 오류 메시지, 진행 제한 등
   실패 상황에 대한 시스템 반응이 명시되어 있으면
   Negative Test를 별도로 검토한다.

9. 정책 또는 업무 조건 자체가 핵심이면 Business Rule을 고려한다.

10. 상태 이동 또는 상태 변화가 핵심이면 State Transition을 고려한다.

11. 플랫폼 간 차이 또는 동일성이 핵심이면 Platform을 고려한다.

12. 인증, 권한, 개인정보 보호가 핵심이면 Security를 고려한다.

13. 정의된 Rule 중 적절한 것이 하나도 없다면
    No Applicable Rule만 선택한다.

최종 선택 전에 반드시 아래를 다시 확인한다:
- 숫자 경계 조건을 놓치지 않았는가?
- 실패 또는 오류 상황을 놓치지 않았는가?
- 서로 다른 검증 목적이 2개 이상인데 하나만 선택하지 않았는가?
- 이미 하나의 Rule을 선택했다는 이유로 다른 핵심 Rule을 누락하지 않았는가?

주의:
- 특정 단어 하나만 보고 Rule을 선택하지 않는다.
- Rule 수를 일부러 늘리지 않는다.
- 요구사항에 직접적인 근거가 있는 Rule만 선택한다.
- No Applicable Rule은 다른 Rule과 동시에 선택하지 않는다.
- JSON 구조는 시스템에서 강제하므로 특정 Rule 예시를 따라 하지 않는다.
- reason은 짧고 구체적으로 작성한다.
- confidence는 0부터 1 사이 숫자로 작성한다.

요구사항:
{requirement}
""".strip()


# ============================================================
# JSON Schema
# ============================================================

OUTPUT_SCHEMA = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "rule": {
                "type": "string",
                "enum": RULES,
            },
            "reason": {
                "type": "string",
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
        },
        "required": [
            "rule",
            "reason",
            "confidence",
        ],
        "additionalProperties": False,
    },
}


# ============================================================
# Result File
# ============================================================

def load_results():

    if not RESULT_FILE.exists():
        return {}

    try:

        with open(
            RESULT_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except json.JSONDecodeError:

        print(
            "⚠️ 기존 결과 파일의 JSON 형식이 올바르지 않습니다."
        )

        return {}


def save_results(results):

    RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# Ollama API
# ============================================================

def call_ollama(prompt: str):

    payload = {
        "model": MODEL_NAME,

        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],

        "stream": False,
        "think": False,

        "format": OUTPUT_SCHEMA,

        "options": {
            "temperature": 0.1,
            "num_predict": 120,

            # 현재 PC 환경에서는 GPU 일부 사용 시
            # runner crash가 발생했으므로 CPU-only 실행
            "num_gpu": 0,
        },
    }

    data = json.dumps(
        payload
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=300,
    ) as response:

        response_body = response.read().decode(
            "utf-8"
        )

        return json.loads(
            response_body
        )


# ============================================================
# Response Parser
# ============================================================

def parse_response(response_data):

    message = response_data.get(
        "message",
        {}
    )

    raw_text = message.get(
        "content",
        ""
    ).strip()

    if not raw_text:

        raise ValueError(
            "Ollama 응답이 비어 있습니다."
        )

    try:

        return json.loads(
            raw_text
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            "Ollama 응답을 JSON으로 변환하지 못했습니다.\n"
            f"Raw Response:\n{raw_text}\n"
            f"JSON Error: {e}"
        )


# ============================================================
# Validation
# ============================================================

def validate_rules(rules):

    if not isinstance(
        rules,
        list,
    ):

        raise ValueError(
            "응답이 JSON 배열 형식이 아닙니다."
        )

    if not rules:

        raise ValueError(
            "선택된 Rule이 없습니다."
        )

    selected_rules = []

    for item in rules:

        if not isinstance(
            item,
            dict,
        ):

            raise ValueError(
                "Rule 항목이 JSON 객체가 아닙니다."
            )

        rule = item.get(
            "rule"
        )

        if rule not in RULES:

            raise ValueError(
                f"정의되지 않은 Rule: {rule}"
            )

        selected_rules.append(
            rule
        )

        reason = item.get(
            "reason"
        )

        if not reason:

            raise ValueError(
                f"{rule}에 reason이 없습니다."
            )

        if "confidence" not in item:

            raise ValueError(
                f"{rule}에 confidence가 없습니다."
            )

        confidence = item[
            "confidence"
        ]

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

    if len(selected_rules) != len(set(selected_rules)):

        raise ValueError(
            "동일한 Rule이 중복 선택되었습니다."
        )

    if (
        "No Applicable Rule"
        in selected_rules
        and len(selected_rules) > 1
    ):

        raise ValueError(
            "No Applicable Rule은 다른 Rule과 동시에 선택할 수 없습니다."
        )


# ============================================================
# Single Case
# ============================================================

def process_case(
    case,
    results,
):

    case_id = case[
        "id"
    ]

    if (
        case_id in results
        and results[
            case_id
        ].get(
            "status"
        ) == "success"
    ):

        print(
            f"[{case_id}] SKIP - 기존 성공 결과 존재"
        )

        return


    print()
    print(
        f"[{case_id}]"
    )

    print(
        f"Requirement : {case['requirement']}"
    )

    print(
        f"Expected    : {case['expected']}"
    )


    prompt = build_prompt(
        case[
            "requirement"
        ]
    )


    start_time = time.perf_counter()


    try:

        response_data = call_ollama(
            prompt
        )


        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        rules = parse_response(
            response_data
        )


        validate_rules(
            rules
        )


        actual = [
            item["rule"]
            for item in rules
        ]


        results[
            case_id
        ] = {

            "model":
                MODEL_NAME,

            "experiment":
                "prompt_v3",

            "prompt_type":
                "multi_rule_boundary_optimized",

            "requirement":
                case[
                    "requirement"
                ],

            "expected":
                case[
                    "expected"
                ],

            "difficulty":
                case.get(
                    "difficulty"
                ),

            "categories":
                case.get(
                    "categories",
                    [],
                ),

            "rules":
                rules,

            "actual":
                actual,

            "elapsed_seconds":
                round(
                    elapsed_time,
                    3,
                ),

            "status":
                "success",
        }


        save_results(
            results
        )


        print(
            f"Ollama      : {actual}"
        )

        print(
            f"Time        : {elapsed_time:.2f}s"
        )

        print(
            "Status      : SUCCESS"
        )


    # ========================================================
    # HTTP Error
    # ========================================================

    except urllib.error.HTTPError as e:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        try:

            error_body = e.read().decode(
                "utf-8",
                errors="ignore",
            )

        except Exception:

            error_body = ""


        results[
            case_id
        ] = {

            "model":
                MODEL_NAME,

            "experiment":
                "prompt_v3",

            "requirement":
                case[
                    "requirement"
                ],

            "expected":
                case[
                    "expected"
                ],

            "actual":
                [],

            "elapsed_seconds":
                round(
                    elapsed_time,
                    3,
                ),

            "status":
                "http_error",

            "http_code":
                e.code,

            "error":
                error_body,
        }


        save_results(
            results
        )


        print(
            "Status      : HTTP ERROR"
        )

        print(
            f"HTTP Code   : {e.code}"
        )

        print(
            f"Time        : {elapsed_time:.2f}s"
        )

        print(
            f"Error Body  : {error_body}"
        )


    # ========================================================
    # Connection Error
    # ========================================================

    except urllib.error.URLError as e:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        results[
            case_id
        ] = {

            "model":
                MODEL_NAME,

            "experiment":
                "prompt_v3",

            "requirement":
                case[
                    "requirement"
                ],

            "expected":
                case[
                    "expected"
                ],

            "actual":
                [],

            "elapsed_seconds":
                round(
                    elapsed_time,
                    3,
                ),

            "status":
                "connection_error",

            "error":
                str(e),
        }


        save_results(
            results
        )


        print(
            "Status      : CONNECTION ERROR"
        )

        print(
            f"Time        : {elapsed_time:.2f}s"
        )

        print(
            f"Error       : {e}"
        )


    # ========================================================
    # Other Error
    # ========================================================

    except Exception as e:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        results[
            case_id
        ] = {

            "model":
                MODEL_NAME,

            "experiment":
                "prompt_v3",

            "requirement":
                case[
                    "requirement"
                ],

            "expected":
                case[
                    "expected"
                ],

            "actual":
                [],

            "elapsed_seconds":
                round(
                    elapsed_time,
                    3,
                ),

            "status":
                "error",

            "error":
                str(e),
        }


        save_results(
            results
        )


        print(
            "Status      : ERROR"
        )

        print(
            f"Time        : {elapsed_time:.2f}s"
        )

        print(
            f"Error       : {e}"
        )


# ============================================================
# Main Analysis
# ============================================================

def analyze_all():

    print(
        "=" * 80
    )

    print(
        "Ollama QA Rule Analysis - Prompt v3"
    )

    print(
        "=" * 80
    )


    print(
        f"Model       : {MODEL_NAME}"
    )

    print(
        "Prompt      : v3 - Multi Rule + Boundary optimized"
    )

    print(
        f"Result File : {RESULT_FILE}"
    )


    results = load_results()


    print(
        f"Saved Cases : {len(results)}"
    )


    total_start = (
        time.perf_counter()
    )


    # 20개 전체 실행
    for case in TEST_DATASET:

        process_case(
            case,
            results,
        )


    total_elapsed = (
        time.perf_counter()
        - total_start
    )


    success_times = [

        data[
            "elapsed_seconds"
        ]

        for data in results.values()

        if (
            data.get(
                "status"
            )
            == "success"

            and data.get(
                "elapsed_seconds"
            )
            is not None
        )
    ]


    print()

    print(
        "=" * 80
    )

    print(
        "Analysis Complete"
    )

    print(
        "=" * 80
    )


    print(
        f"전체 실행 시간   : {total_elapsed:.2f}s"
    )


    if success_times:

        average_time = (
            sum(
                success_times
            )
            / len(
                success_times
            )
        )


        print(
            f"평균 처리 시간   : {average_time:.2f}s"
        )

        print(
            f"최소 처리 시간   : {min(success_times):.2f}s"
        )

        print(
            f"최대 처리 시간   : {max(success_times):.2f}s"
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    analyze_all()