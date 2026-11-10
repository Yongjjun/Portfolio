
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from evaluate_rules import TEST_DATASET


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RESULT_FILES = {
    "gemini": DATA_DIR / "llm_results.json",
    "ollama": DATA_DIR / "ollama_qwen3_1.7b_schema_results.json",
    "ollama_v3": DATA_DIR / "ollama_qwen3_1.7b_v3_results.json",
    "v2_controlled": DATA_DIR / "ollama_v2_controlled_results.json",
    "v4_controlled": DATA_DIR / "ollama_v4_controlled_results.json",
}

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
    "No Applicable Rule",
]

CASES = {case["id"]: case for case in TEST_DATASET}


def load_results(provider):
    path = RESULT_FILES[provider]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("결과 파일은 케이스 ID를 키로 가진 객체여야 합니다.")
    return data


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f1


def classification(expected, actual):
    missing = set(expected) - set(actual)
    extra = set(actual) - set(expected)

    if not missing and not extra:
        return "exact"
    if extra and not missing:
        return "over_selection"
    if missing and not extra:
        return "under_selection"
    return "mixed_error"


def get_output_issue(result):
    """실패 상태를 연결/API/출력 유효성 오류로 구분."""
    status = result.get("status", "unknown")
    error = str(result.get("error", "")).lower()

    if status == "success":
        return None
    if status in ("http_error", "connection_error",
                  "rate_limit", "service_unavailable"):
        return "infrastructure_error"
    if status == "validation_error":
        return "output_validation_error"
    if any(token in error for token in (
        "json", "rule", "confidence", "배열",
        "중복", "동시에 선택"
    )):
        return "output_validation_error"
    return "other_execution_error"


def validate_saved_success(result):
    """이미 성공으로 저장된 결과도 다시 형식 검증."""
    actual = result.get("actual")

    if not isinstance(actual, list) or not actual:
        return "actual이 비어 있거나 배열이 아닙니다."

    if any(not isinstance(rule, str) or rule not in RULES
           for rule in actual):
        return "정의되지 않은 Rule이 포함되어 있습니다."

    if len(set(actual)) != len(actual):
        return "동일 Rule이 중복 선택되었습니다."

    if "No Applicable Rule" in actual and len(actual) > 1:
        return "No Applicable Rule 조합 규칙 위반"

    rule_objects = result.get("rules")
    if rule_objects is not None:
        if not isinstance(rule_objects, list):
            return "rules가 배열이 아닙니다."
        if [item.get("rule") for item in rule_objects
                if isinstance(item, dict)] != actual:
            return "rules와 actual 불일치"
        for item in rule_objects:
            if not isinstance(item, dict):
                return "Rule 객체 형식 오류"
            if not isinstance(item.get("reason"), str) or not item["reason"].strip():
                return "reason 누락"
            c = item.get("confidence")
            if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0 <= c <= 1:
                return "confidence 형식/범위 오류"

    return None


def evaluate(provider, raw_results):
    rows = []
    success_rows = []
    errors = Counter()
    counts = Counter()
    rule_stats = defaultdict(Counter)
    difficulty_stats = defaultdict(Counter)
    composition_stats = defaultdict(Counter)
    latency = []

    tp = fp = fn = 0

    for case in TEST_DATASET:
        cid = case["id"]
        expected = list(case["expected"])
        difficulty = case.get("difficulty", "Unknown")
        composition = "single" if len(expected) == 1 else "multi"
        result = raw_results.get(cid)

        row = {
            "id": cid,
            "difficulty": difficulty,
            "composition": composition,
            "requirement": case["requirement"],
            "expected": ", ".join(expected),
            "actual": "",
            "status": "not_executed",
            "classification": "NOT_EXECUTED",
            "error_type": "",
            "error": "",
            "elapsed_seconds": "",
        }

        counts["total"] += 1

        if result is None:
            counts["not_executed"] += 1
            rows.append(row)
            continue

        counts["attempted"] += 1
        status = result.get("status", "unknown")
        issue = get_output_issue(result)

        if issue is None:
            validation_error = validate_saved_success(result)
            if validation_error:
                issue = "output_validation_error"
                row["error"] = validation_error

        if issue is not None:
            counts["failed"] += 1
            errors[issue] += 1
            row.update({
                "status": status,
                "classification": "INVALID_OUTPUT"
                    if issue == "output_validation_error"
                    else "EXECUTION_ERROR",
                "error_type": issue,
                "error": row["error"] or str(result.get("error", "")),
                "elapsed_seconds": result.get("elapsed_seconds", ""),
            })
            rows.append(row)
            continue

        actual = list(result["actual"])
        kind = classification(expected, actual)

        counts["valid"] += 1
        counts[kind] += 1
        difficulty_stats[difficulty]["valid"] += 1
        difficulty_stats[difficulty][kind] += 1
        composition_stats[composition]["valid"] += 1
        composition_stats[composition][kind] += 1

        expected_set = set(expected)
        actual_set = set(actual)

        tp += len(expected_set & actual_set)
        fp += len(actual_set - expected_set)
        fn += len(expected_set - actual_set)

        for rule in expected_set:
            rule_stats[rule]["expected"] += 1
            if rule in actual_set:
                rule_stats[rule]["correct"] += 1
            else:
                rule_stats[rule]["missing"] += 1

        for rule in actual_set:
            rule_stats[rule]["selected"] += 1
            if rule not in expected_set:
                rule_stats[rule]["extra"] += 1

        elapsed = result.get("elapsed_seconds")
        if isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool):
            latency.append(elapsed)

        row.update({
            "actual": ", ".join(actual),
            "status": "success",
            "classification": kind,
            "elapsed_seconds": elapsed if elapsed is not None else "",
        })
        rows.append(row)
        success_rows.append((cid, expected, actual))

    p, r, f1 = prf(tp, fp, fn)

    rules_summary = {}
    for rule in RULES:
        stat = rule_stats[rule]
        rp, rr, rf = prf(
            stat["correct"], stat["extra"], stat["missing"]
        )
        rules_summary[rule] = {
            **dict(stat),
            "precision": rp,
            "recall": rr,
            "f1": rf,
        }

    summary = {
        "provider": provider,
        "dataset_cases": counts["total"],
        "attempted": counts["attempted"],
        "valid": counts["valid"],
        "failed": counts["failed"],
        "not_executed": counts["not_executed"],
        "valid_output_rate": (
            counts["valid"] / counts["attempted"]
            if counts["attempted"] else 0
        ),
        "error_types": dict(errors),
        "exact": counts["exact"],
        "over_selection": counts["over_selection"],
        "under_selection": counts["under_selection"],
        "mixed_error": counts["mixed_error"],
        "exact_accuracy": (
            counts["exact"] / counts["valid"] if counts["valid"] else 0
        ),
        "precision": p,
        "recall": r,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "difficulty": {
            k: {
                **dict(v),
                "accuracy": v["exact"] / v["valid"] if v["valid"] else 0,
            }
            for k, v in difficulty_stats.items()
        },
        "composition": {
            k: {
                **dict(v),
                "accuracy": v["exact"] / v["valid"] if v["valid"] else 0,
            }
            for k, v in composition_stats.items()
        },
        "rules": rules_summary,
        "latency": {
            "count": len(latency),
            "avg": sum(latency) / len(latency) if latency else None,
            "min": min(latency) if latency else None,
            "max": max(latency) if latency else None,
        },
    }

    return summary, rows, success_rows


def save_report(provider, summary, rows):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = DATA_DIR / f"{provider}_evaluation_summary_v2.json"
    detail_path = DATA_DIR / f"{provider}_evaluation_details_v2.csv"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(detail_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    return summary_path, detail_path


def print_report(summary):
    print(f"\n=== {summary['provider'].upper()} 평가 ===")
    print(f"전체: {summary['dataset_cases']}건")
    print(f"유효 출력: {summary['valid']}건")
    print(f"실패: {summary['failed']}건")
    print(f"미실행: {summary['not_executed']}건")
    print(f"출력 유효율: {summary['valid_output_rate']:.2%}")
    print(f"오류 유형: {summary['error_types']}")

    print(f"\nExact Match: {summary['exact']}건 "
          f"({summary['exact_accuracy']:.2%})")
    print(f"Precision: {summary['precision']:.2%}")
    print(f"Recall: {summary['recall']:.2%}")
    print(f"F1: {summary['f1']:.2%}")
    print("오류 분류:",
          {k: summary[k] for k in (
              "over_selection", "under_selection", "mixed_error"
          )})

    print("\n[단일/복수 Rule]")

    for key, stat in summary["composition"].items():

        exact = stat.get("exact", 0)
        valid = stat.get("valid", 0)
        accuracy = stat.get("accuracy", 0.0)

        print(
            f"{key}: {exact}/{valid} "
            f"({accuracy:.2%})"
        )

    print("\n[Rule별 결과: 유효 출력 기준]")
    for rule, stat in summary["rules"].items():
        if stat.get("expected", 0) == 0 and stat.get("selected", 0) == 0:
            continue
        print(f"{rule:<22} "
              f"P={stat['precision']:.2%} "
              f"R={stat['recall']:.2%} "
              f"Missing={stat.get('missing', 0)} "
              f"Extra={stat.get('extra', 0)}")


def compare(provider_a, provider_b):
    raw_a = load_results(provider_a)
    raw_b = load_results(provider_b)

    valid_a = {
        cid: row for cid, _, row in evaluate(provider_a, raw_a)[2]
    }
    valid_b = {
        cid: row for cid, _, row in evaluate(provider_b, raw_b)[2]
    }

    shared = sorted(set(valid_a) & set(valid_b))
    a_correct = 0
    b_correct = 0
    changes = []

    for cid in shared:
        expected = set(CASES[cid]["expected"])
        a_ok = set(valid_a[cid]) == expected
        b_ok = set(valid_b[cid]) == expected

        a_correct += a_ok
        b_correct += b_ok

        if a_ok != b_ok:
            changes.append({
                "id": cid,
                "expected": CASES[cid]["expected"],
                provider_a: valid_a[cid],
                provider_b: valid_b[cid],
                "winner": provider_a if a_ok else provider_b,
            })

    n = len(shared)
    print(f"\n=== 공통 유효 케이스 비교: {provider_a} vs {provider_b} ===")
    print(f"공통 케이스: {n}건")
    print(f"{provider_a}: {a_correct}/{n} "
          f"({a_correct / n:.2%})" if n else f"{provider_a}: 평가 불가")
    print(f"{provider_b}: {b_correct}/{n} "
          f"({b_correct / n:.2%})" if n else f"{provider_b}: 평가 불가")

    print("\n정확/오답 여부가 달라진 케이스:")
    for item in changes:
        print(f"  {item['id']}: {item['winner']} 우세")

    path = DATA_DIR / f"compare_{provider_a}_vs_{provider_b}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "providers": [provider_a, provider_b],
            "common_valid_cases": n,
            "exact": {
                provider_a: a_correct,
                provider_b: b_correct,
            },
            "changed_cases": changes,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n비교 결과 저장: {path}")


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "compare":
        a, b = sys.argv[2], sys.argv[3]
        if a not in RESULT_FILES or b not in RESULT_FILES:
            raise ValueError("등록되지 않은 결과 파일입니다.")
        compare(a, b)
        return

    if len(sys.argv) != 2 or sys.argv[1] not in RESULT_FILES:
        print("사용법:")
        print("  python evaluate_llm_results.py v2_controlled")
        print("  python evaluate_llm_results.py v4_controlled")
        print("  python evaluate_llm_results.py compare v2_controlled v4_controlled")
        return

    provider = sys.argv[1]
    summary, rows, _ = evaluate(provider, load_results(provider))
    print_report(summary)

    p1, p2 = save_report(provider, summary, rows)
    print(f"\n저장: {p1}")
    print(f"저장: {p2}")


if __name__ == "__main__":
    main()
