
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from evaluate_rules import TEST_DATASET
import ollama_analyzer_v2 as v2


# ============================================================
# 공통 설정: v2와 v4가 동일하게 사용
# ============================================================

MODEL_NAME = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

EXPERIMENT_FILES = {
    "v2": DATA_DIR / "ollama_v2_controlled_results.json",
    "v4": DATA_DIR / "ollama_v4_controlled_results.json",
}

TEMPERATURE = 0.1
NUM_PREDICT = 384
NUM_GPU = 0

# 기존 v2의 Rule 정의와 JSON Schema 재사용
OUTPUT_SCHEMA = v2.OUTPUT_SCHEMA
RULES = v2.RULES


# ============================================================
# Prompt v2 / v4
# ============================================================

def build_prompt(requirement, version):

    # 기존 v2 프롬프트를 기준으로 사용
    original_prompt = v2.build_prompt(requirement)

    if version == "v2":
        return original_prompt

    # v4: v2의 Rule 정의는 유지하고
    # 독립 검토 및 제외 기준만 보강
    extra_instruction = """
추가 검토 지침:

1. 먼저 요구사항의 핵심 검증 목적을 식별한다.

2. 각 Rule에 대해 요구사항에 직접적인 근거가
   있는지 독립적으로 확인한다.

3. 명시적인 최소/최대/범위 조건이 있다면
   Boundary Value의 적용 여부를 별도로 판단한다.
   단, 숫자가 있다는 이유만으로 선택하지 않는다.

4. 서로 다른 검증 목적이 명확하게 두 개 이상이라면
   복수 Rule을 선택할 수 있다.
   단순히 연관성이 있다는 이유로 추가하지 않는다.

5. 선택하려는 Rule에 대해 다음을 확인한다.
   - 선택 조건을 충족하는가?
   - 제외 조건에 해당하지 않는가?
   - 요구사항에 없는 상황을 가정하지 않았는가?

6. 직접 적용할 수 있는 Rule이 없다면
   No Applicable Rule만 선택한다.

7. 선택한 각 Rule의 reason은
   요구사항에 나타난 근거만 짧게 설명한다.
"""

    # 기존 프롬프트에서 요구사항 바로 앞에
    # 추가 검토 지침을 배치
    marker = (
        "============================================================\n"
        "REQUIREMENT"
    )

    if marker in original_prompt:
        return original_prompt.replace(
            marker,
            extra_instruction + "\n\n" + marker,
            1,
        )

    # 기존 프롬프트 형식이 다른 경우에도
    # 동작하도록, 요구사항을 마지막에 다시 명시
    return (
        original_prompt
        + "\n\n"
        + extra_instruction
        + "\n\n최종 분석 대상 요구사항:\n"
        + requirement
    )


# ============================================================
# Ollama API
# ============================================================

def call_ollama(prompt):

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
            "temperature": TEMPERATURE,
            "num_predict": NUM_PREDICT,
            "num_gpu": NUM_GPU,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=300,
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


# ============================================================
# 결과 저장 및 검증
# ============================================================

def load_results(path):

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(path, results):

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )


def process_case(case, version, results, path):

    case_id = case["id"]

    if results.get(case_id, {}).get("status") == "success":
        print(f"[{case_id}] SKIP")
        return

    print(f"\n[{case_id}] {case['requirement']}")
    print(f"Expected : {case['expected']}")

    prompt = build_prompt(case["requirement"], version)
    start = time.perf_counter()

    result = {
        "model": MODEL_NAME,
        "experiment": f"controlled_{version}",
        "requirement": case["requirement"],
        "expected": case["expected"],
        "difficulty": case.get("difficulty"),
        "categories": case.get("categories", []),
        "actual": [],
        "status": "error",
        "settings": {
            "temperature": TEMPERATURE,
            "num_predict": NUM_PREDICT,
            "num_gpu": NUM_GPU,
        },
    }

    try:
        response = call_ollama(prompt)
        raw_text = response.get("message", {}).get(
            "content", ""
        )

        rules = json.loads(raw_text)

        # 기존 v2의 출력 검증 재사용
        v2.validate_rules(rules)

        actual = [item["rule"] for item in rules]

        # 중복 선택 여부 추가 검증
        if len(actual) != len(set(actual)):
            raise ValueError("동일 Rule 중복 선택")

        result.update({
            "status": "success",
            "rules": rules,
            "actual": actual,
            "raw_response": raw_text,
            "done_reason": response.get("done_reason"),
        })

        print(f"Actual   : {actual}")
        print("Status   : SUCCESS")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode(
            "utf-8", errors="replace"
        )
        result["status"] = "http_error"
        result["error"] = f"HTTP {e.code}: {error_body}"
        print(f"HTTP ERROR: {result['error']}")

    except urllib.error.URLError as e:
        result["status"] = "connection_error"
        result["error"] = str(e)
        print(f"CONNECTION ERROR: {e}")

    except (ValueError, json.JSONDecodeError) as e:
        result["status"] = "validation_error"
        result["error"] = str(e)

        if "raw_text" in locals():
            result["raw_response"] = raw_text

        print(f"VALIDATION ERROR: {e}")

    except Exception as e:
        result["error"] = str(e)
        print(f"ERROR: {e}")

    finally:
        result["elapsed_seconds"] = round(
            time.perf_counter() - start, 3
        )

        results[case_id] = result
        save_results(path, results)

        print(
            f"Time     : {result['elapsed_seconds']:.2f}s"
        )


# ============================================================
# 실험 실행
# ============================================================

def main():

    if len(sys.argv) < 2 or sys.argv[1] not in ("v2", "v4"):
        print("사용법: python run_ab_experiment.py v2")
        print("        python run_ab_experiment.py v4")
        sys.exit(1)

    version = sys.argv[1]
    result_file = EXPERIMENT_FILES[version]

    print("=" * 70)
    print(f"QA Co-Pilot Controlled Experiment - {version.upper()}")
    print("=" * 70)
    print(f"Model       : {MODEL_NAME}")
    print(f"Temperature : {TEMPERATURE}")
    print(f"Num Predict : {NUM_PREDICT}")
    print(f"CPU-only    : {NUM_GPU == 0}")
    print(f"Result File : {result_file}")

    results = load_results(result_file)

    # 첫 실행은 3개만 테스트
    # 정상 동작 확인 후 TEST_DATASET으로 변경
    for case in TEST_DATASET:
        process_case(case, version, results, result_file)

    success = sum(
        1 for item in results.values()
        if item.get("status") == "success"
    )

    print("\n" + "=" * 70)
    print(f"저장된 성공 결과: {success}/{len(TEST_DATASET)}")
    print(f"결과 파일: {result_file}")


if __name__ == "__main__":
    main()