import json
from pathlib import Path

from evaluate_rules import TEST_DATASET


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_FILE = BASE_DIR / "data" / "llm_results.json"


# ============================================================
# Load Saved Gemini Results
# ============================================================

def load_results():
    """저장된 Gemini 분석 결과를 불러온다."""

    if not RESULT_FILE.exists():
        print(f"❌ 결과 파일을 찾을 수 없습니다: {RESULT_FILE}")
        return {}

    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Metrics
# ============================================================

def calculate_metrics(expected, actual):

    expected = set(expected)
    actual = set(actual)

    true_positive = len(expected & actual)
    false_positive = len(actual - expected)
    false_negative = len(expected - actual)

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive > 0
        else 0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative > 0
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0
    )

    exact_match = expected == actual

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact_match,
    }


# ============================================================
# Evaluation
# ============================================================

def evaluate_llm():

    saved_results = load_results()

    if not saved_results:
        return

    results = []

    evaluated_cases = 0
    skipped_cases = 0

    for case in TEST_DATASET:

        case_id = case["id"]

        print(f"\n[{case_id}]")
        print(f"Requirement : {case['requirement']}")
        print(f"Expected    : {case['expected']}")

        # ----------------------------------------------------
        # 저장된 Gemini 결과 확인
        # ----------------------------------------------------

        if case_id not in saved_results:

            print("Gemini      : SKIP - 결과 없음")
            skipped_cases += 1
            continue

        saved_case = saved_results[case_id]

        # ----------------------------------------------------
        # API 오류 결과는 평가에서 제외
        # ----------------------------------------------------

        if saved_case.get("status") != "success":

            print(
                f"Gemini      : SKIP - "
                f"status={saved_case.get('status')}"
            )

            skipped_cases += 1
            continue

        # ----------------------------------------------------
        # 저장된 Gemini 결과 사용
        # ----------------------------------------------------

        actual = saved_case.get("actual", [])

        metrics = calculate_metrics(
            case["expected"],
            actual
        )

        print(f"Gemini      : {actual}")
        print(f"Precision   : {metrics['precision']:.2%}")
        print(f"Recall      : {metrics['recall']:.2%}")
        print(f"F1 Score    : {metrics['f1']:.2%}")
        print(f"Exact Match : {metrics['exact_match']}")

        results.append(metrics)

        evaluated_cases += 1

    # ========================================================
    # Summary
    # ========================================================

    if not results:
        print("\n평가할 수 있는 결과가 없습니다.")
        return

    avg_precision = sum(
        result["precision"]
        for result in results
    ) / len(results)

    avg_recall = sum(
        result["recall"]
        for result in results
    ) / len(results)

    avg_f1 = sum(
        result["f1"]
        for result in results
    ) / len(results)

    exact_matches = sum(
        result["exact_match"]
        for result in results
    )

    print("\n" + "=" * 80)
    print("Gemini Evaluation Summary")
    print("=" * 80)

    print(f"Total Dataset     : {len(TEST_DATASET)}")
    print(f"Evaluated Cases   : {evaluated_cases}")
    print(f"Skipped Cases     : {skipped_cases}")
    print(f"Exact Match       : {exact_matches}/{evaluated_cases}")
    print(
        f"Exact Match Rate  : "
        f"{exact_matches / evaluated_cases:.2%}"
    )
    print(f"Average Precision : {avg_precision:.2%}")
    print(f"Average Recall    : {avg_recall:.2%}")
    print(f"Average F1 Score  : {avg_f1:.2%}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    evaluate_llm()