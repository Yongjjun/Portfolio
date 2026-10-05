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
    / "ollama_qwen3_1.7b_compressed_results.json"
)


# ============================================================
# Compact Rule Definitions
# ============================================================

RULE_DEFINITIONS = {
    "Validation":
        "입력값 형식 또는 필수 여부 검증. "
        "단순 값 언급만으로 선택하지 않음.",

    "Boundary Value":
        "최소값, 최대값, 범위 등 명시적 경계 조건 검증.",

    "Equivalence Partition":
        "입력값을 유효/무효 등 대표 그룹으로 나눠 검증.",

    "Negative Test":
        "잘못된 입력이나 실패 상황에 대한 시스템 반응 검증. "
        "단순 불가 조건만으로 선택하지 않음.",

    "Business Rule":
        "서비스 정책 또는 업무 조건 자체를 검증.",

    "State Transition":
        "명확한 상태 변화 또는 상태 간 이동 검증.",

    "Regression":
        "기존 기능 변경으로 인한 영향이나 회귀 검증이 명시된 경우.",

    "Platform":
        "Web, Android, iOS 등 플랫폼 간 차이 또는 동일성 검증.",

    "Accessibility":
        "접근성 기능이나 사용성 보장이 명시된 경우.",

    "Security":
        "인증, 권한, 개인정보 보호 자체가 검증 대상인 경우.",

    "No Applicable Rule":
        "현재 정의된 Rule 중 핵심 목적에 직접 해당하는 Rule이 없는 경우.",
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

아래 요구사항의 핵심 검증 목적에 직접 해당하는 QA Rule만 선택하라.

QA Rule:
{rule_text}

선택 원칙:
1. 핵심 검증 목적에 직접 해당하는 Rule만 선택한다.
2. 요구사항에 없는 내용을 추론해 Rule을 추가하지 않는다.
3. 복수 Rule은 명확히 필요한 경우에만 선택한다.
4. 수치의 최소/최대/범위가 핵심이면 Boundary Value를 고려한다.
5. 정책/업무 조건이면 Business Rule을 고려한다.
6. 상태 이동이 핵심이면 State Transition을 고려한다.
7. 인증/권한/개인정보 보호가 핵심이면 Security를 고려한다.
8. 적절한 Rule이 없으면 No Applicable Rule만 선택한다.

반드시 JSON 배열만 반환한다.
Markdown과 설명문은 출력하지 않는다.

응답 형식:
[
  {{
    "rule": "Boundary Value",
    "reason": "명시적인 최소값 경계 조건이 있기 때문",
    "confidence": 0.95
  }}
]

요구사항:
{requirement}
""".strip()


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

        "options": {
            "temperature": 0.1,
            "num_predict": 80,
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


    if raw_text.startswith("```"):

        raw_text = raw_text.replace(
            "```json",
            "",
            1,
        )

        raw_text = raw_text.replace(
            "```",
            "",
        ).strip()


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


    if (
        "No Applicable Rule"
        in selected_rules
        and len(
            selected_rules
        ) > 1
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

    case_id = case["id"]


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


    start_time = (
        time.perf_counter()
    )


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

            "prompt_type":
                "compressed",

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

            "prompt_type":
                "compressed",

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

            "prompt_type":
                "compressed",

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

            "prompt_type":
                "compressed",

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
        "Ollama QA Rule Analysis - Compressed Prompt"
    )

    print(
        "=" * 80
    )


    print(
        f"Model       : {MODEL_NAME}"
    )

    print(
        "Prompt      : compressed"
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


    # 우선 TC-001 하나만 실행
    for case in TEST_DATASET[:1]:

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