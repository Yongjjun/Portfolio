import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from evaluate_rules import TEST_DATASET


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


ALL_RULES = [
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


RESULT_FILES = {
    "gemini": DATA_DIR / "llm_results.json",

    "ollama": (
        DATA_DIR
        / "ollama_qwen3_1.7b_schema_results.json"
        
    ),

    "ollama_v3": (
    DATA_DIR
    / "ollama_qwen3_1.7b_v3_results.json"
),

    
}


# ============================================================
# Provider
# ============================================================

def get_provider():

    if len(sys.argv) < 2:

        print(
            "사용법:"
        )

        print(
            "python evaluate_llm_results.py ollama"
        )

        print(
            "또는"
        )

        print(
            "python evaluate_llm_results.py gemini"
        )

        sys.exit(1)


    provider = (
        sys.argv[1]
        .strip()
        .lower()
    )


    if provider not in RESULT_FILES:

        print(
            f"지원하지 않는 provider: {provider}"
        )

        print(
                "사용 가능: gemini, ollama, ollama_v3"
        )

        sys.exit(1)


    return provider


# ============================================================
# Load Results
# ============================================================

def load_results(result_file):

    if not result_file.exists():

        raise FileNotFoundError(
            f"결과 파일이 없습니다:\n{result_file}"
        )


    with open(
        result_file,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# Classification
# ============================================================

def classify_result(
    expected,
    actual,
):

    expected_set = set(
        expected
    )

    actual_set = set(
        actual
    )


    missing = (
        expected_set
        - actual_set
    )

    extra = (
        actual_set
        - expected_set
    )


    if (
        not missing
        and not extra
    ):

        return "exact"


    if (
        not missing
        and extra
    ):

        return "over_selection"


    if (
        missing
        and not extra
    ):

        return "under_selection"


    return "mixed_error"


# ============================================================
# Metrics
# ============================================================

def calculate_case_metrics(
    expected,
    actual,
):

    expected_set = set(
        expected
    )

    actual_set = set(
        actual
    )


    tp = len(
        expected_set
        & actual_set
    )

    fp = len(
        actual_set
        - expected_set
    )

    fn = len(
        expected_set
        - actual_set
    )


    return tp, fp, fn


def calculate_prf(
    tp,
    fp,
    fn,
):

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )

    f1 = (
        2
        * precision
        * recall
        / (
            precision
            + recall
        )
        if (
            precision
            + recall
        ) > 0
        else 0
    )


    return (
        precision,
        recall,
        f1,
    )


# ============================================================
# Evaluation
# ============================================================

def evaluate(
    provider,
    results,
):

    total = len(
        TEST_DATASET
    )

    executed = 0
    success = 0
    failed = 0
    not_executed = 0

    exact = 0
    over = 0
    under = 0
    mixed = 0

    total_tp = 0
    total_fp = 0
    total_fn = 0


    difficulty_stats = defaultdict(
        lambda: {
            "total": 0,
            "success": 0,
            "failed": 0,
            "not_executed": 0,

            "exact": 0,
            "over_selection": 0,
            "under_selection": 0,
            "mixed_error": 0,

            "tp": 0,
            "fp": 0,
            "fn": 0,
        }
    )


    rule_stats = {
        rule: {
            "expected_count": 0,
            "selected_count": 0,
            "correct_count": 0,
            "missing_count": 0,
            "extra_count": 0,
        }

        for rule in ALL_RULES
    }


    composition_stats = {
        "single": {
            "total": 0,
            "success": 0,
            "exact": 0,
        },

        "multi": {
            "total": 0,
            "success": 0,
            "exact": 0,
        },
    }


    latency_values = []

    details = []


    for case in TEST_DATASET:

        case_id = case[
            "id"
        ]

        expected = case[
            "expected"
        ]

        difficulty = case.get(
            "difficulty",
            "Unknown",
        )


        composition = (
            "single"
            if len(
                expected
            ) == 1
            else "multi"
        )


        difficulty_stats[
            difficulty
        ][
            "total"
        ] += 1


        composition_stats[
            composition
        ][
            "total"
        ] += 1


        for rule in expected:

            if rule not in rule_stats:
                rule_stats[
                    rule
                ] = {
                    "expected_count": 0,
                    "selected_count": 0,
                    "correct_count": 0,
                    "missing_count": 0,
                    "extra_count": 0,
                }

            rule_stats[
                rule
            ][
                "expected_count"
            ] += 1


        result = results.get(
            case_id
        )


        if result is None:

            not_executed += 1

            difficulty_stats[
                difficulty
            ][
                "not_executed"
            ] += 1


            details.append({
                "id": case_id,
                "difficulty": difficulty,
                "composition": composition,
                "requirement": case[
                    "requirement"
                ],
                "expected": ", ".join(
                    expected
                ),
                "actual": "",
                "classification":
                    "NOT_EXECUTED",
                "status":
                    "not_executed",
                "elapsed_seconds":
                    "",
            })

            continue


        executed += 1


        status = result.get(
            "status"
        )


        if status != "success":

            failed += 1

            difficulty_stats[
                difficulty
            ][
                "failed"
            ] += 1


            details.append({
                "id": case_id,
                "difficulty": difficulty,
                "composition": composition,
                "requirement": case[
                    "requirement"
                ],
                "expected": ", ".join(
                    expected
                ),
                "actual": "",
                "classification":
                    "EXECUTION_ERROR",
                "status":
                    status,
                "elapsed_seconds":
                    result.get(
                        "elapsed_seconds",
                        "",
                    ),
            })

            continue


        success += 1

        difficulty_stats[
            difficulty
        ][
            "success"
        ] += 1


        composition_stats[
            composition
        ][
            "success"
        ] += 1


        actual = result.get(
            "actual",
            [],
        )


        elapsed = result.get(
            "elapsed_seconds"
        )


        if isinstance(
            elapsed,
            (int, float),
        ):

            latency_values.append(
                elapsed
            )


        classification = classify_result(
            expected,
            actual,
        )


        tp, fp, fn = (
            calculate_case_metrics(
                expected,
                actual,
            )
        )


        total_tp += tp
        total_fp += fp
        total_fn += fn


        difficulty_stats[
            difficulty
        ][
            "tp"
        ] += tp

        difficulty_stats[
            difficulty
        ][
            "fp"
        ] += fp

        difficulty_stats[
            difficulty
        ][
            "fn"
        ] += fn


        if classification == "exact":

            exact += 1

            difficulty_stats[
                difficulty
            ][
                "exact"
            ] += 1

            composition_stats[
                composition
            ][
                "exact"
            ] += 1


        elif (
            classification
            == "over_selection"
        ):

            over += 1

            difficulty_stats[
                difficulty
            ][
                "over_selection"
            ] += 1


        elif (
            classification
            == "under_selection"
        ):

            under += 1

            difficulty_stats[
                difficulty
            ][
                "under_selection"
            ] += 1


        else:

            mixed += 1

            difficulty_stats[
                difficulty
            ][
                "mixed_error"
            ] += 1


        expected_set = set(
            expected
        )

        actual_set = set(
            actual
        )


        for rule in actual_set:

            if rule not in rule_stats:

                rule_stats[
                    rule
                ] = {
                    "expected_count": 0,
                    "selected_count": 0,
                    "correct_count": 0,
                    "missing_count": 0,
                    "extra_count": 0,
                }


            rule_stats[
                rule
            ][
                "selected_count"
            ] += 1


        for rule in ALL_RULES:

            if (
                rule in expected_set
                and rule in actual_set
            ):

                rule_stats[
                    rule
                ][
                    "correct_count"
                ] += 1


            elif (
                rule in expected_set
                and rule not in actual_set
            ):

                rule_stats[
                    rule
                ][
                    "missing_count"
                ] += 1


            elif (
                rule not in expected_set
                and rule in actual_set
            ):

                rule_stats[
                    rule
                ][
                    "extra_count"
                ] += 1


        details.append({
            "id":
                case_id,

            "difficulty":
                difficulty,

            "composition":
                composition,

            "requirement":
                case[
                    "requirement"
                ],

            "expected":
                ", ".join(
                    expected
                ),

            "actual":
                ", ".join(
                    actual
                ),

            "classification":
                classification,

            "status":
                status,

            "elapsed_seconds":
                elapsed
                if elapsed is not None
                else "",
        })


    # ========================================================
    # Overall Metrics
    # ========================================================

    precision, recall, f1 = (
        calculate_prf(
            total_tp,
            total_fp,
            total_fn,
        )
    )


    exact_accuracy = (
        exact / success
        if success > 0
        else 0
    )


    # ========================================================
    # Difficulty Metrics
    # ========================================================

    difficulty_summary = {}


    for difficulty, stats in (
        difficulty_stats.items()
    ):

        p, r, f = calculate_prf(
            stats[
                "tp"
            ],
            stats[
                "fp"
            ],
            stats[
                "fn"
            ],
        )


        difficulty_summary[
            difficulty
        ] = {
            **stats,

            "exact_accuracy":
                (
                    stats[
                        "exact"
                    ]
                    / stats[
                        "success"
                    ]
                    if stats[
                        "success"
                    ] > 0
                    else 0
                ),

            "precision":
                p,

            "recall":
                r,

            "f1":
                f,
        }


    # ========================================================
    # Rule Metrics
    # ========================================================

    rule_summary = {}


    for rule, stats in (
        rule_stats.items()
    ):

        selected_count = stats[
            "selected_count"
        ]

        expected_count = stats[
            "expected_count"
        ]

        correct_count = stats[
            "correct_count"
        ]


        rule_precision = (
            correct_count
            / selected_count
            if selected_count > 0
            else 0
        )


        rule_recall = (
            correct_count
            / expected_count
            if expected_count > 0
            else 0
        )


        rule_summary[
            rule
        ] = {
            **stats,

            "precision":
                rule_precision,

            "recall":
                rule_recall,
        }


    # ========================================================
    # Composition Metrics
    # ========================================================

    composition_summary = {}


    for name, stats in (
        composition_stats.items()
    ):

        composition_summary[
            name
        ] = {
            **stats,

            "exact_accuracy":
                (
                    stats[
                        "exact"
                    ]
                    / stats[
                        "success"
                    ]
                    if stats[
                        "success"
                    ] > 0
                    else 0
                ),
        }


    # ========================================================
    # Latency Metrics
    # ========================================================

    if latency_values:

        latency_summary = {
            "count":
                len(
                    latency_values
                ),

            "average_seconds":
                sum(
                    latency_values
                )
                / len(
                    latency_values
                ),

            "min_seconds":
                min(
                    latency_values
                ),

            "max_seconds":
                max(
                    latency_values
                ),
        }

    else:

        latency_summary = {
            "count": 0,
            "average_seconds": 0,
            "min_seconds": 0,
            "max_seconds": 0,
        }


    summary = {
        "provider":
            provider,

        "total_cases":
            total,

        "executed_cases":
            executed,

        "success_cases":
            success,

        "failed_cases":
            failed,

        "not_executed_cases":
            not_executed,

        "exact_match":
            exact,

        "over_selection":
            over,

        "under_selection":
            under,

        "mixed_error":
            mixed,

        "exact_accuracy":
            exact_accuracy,

        "precision":
            precision,

        "recall":
            recall,

        "f1":
            f1,

        "tp":
            total_tp,

        "fp":
            total_fp,

        "fn":
            total_fn,

        "latency":
            latency_summary,

        "difficulty":
            difficulty_summary,

        "composition":
            composition_summary,

        "rules":
            rule_summary,
    }


    return (
        summary,
        details,
    )


# ============================================================
# Save
# ============================================================

def save_summary(
    provider,
    summary,
):

    file_path = (
        DATA_DIR
        / f"{provider}_evaluation_summary.json"
    )


    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=2,
        )


    return file_path


def save_details(
    provider,
    details,
):

    file_path = (
        DATA_DIR
        / f"{provider}_evaluation_details.csv"
    )


    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "difficulty",
                "composition",
                "requirement",
                "expected",
                "actual",
                "classification",
                "status",
                "elapsed_seconds",
            ],
        )

        writer.writeheader()

        writer.writerows(
            details
        )


    return file_path


# ============================================================
# Console Report
# ============================================================

def print_report(
    provider,
    summary,
):

    print()
    print(
        "=" * 80
    )

    print(
        f"LLM Evaluation Report - {provider.upper()}"
    )

    print(
        "=" * 80
    )


    print()
    print(
        "[Overall]"
    )

    print(
        f"전체 케이스       : {summary['total_cases']}"
    )

    print(
        f"성공 실행         : {summary['success_cases']}"
    )

    print(
        f"실행 실패         : {summary['failed_cases']}"
    )

    print(
        f"미실행            : {summary['not_executed_cases']}"
    )


    print()
    print(
        f"Exact Match       : {summary['exact_match']}"
    )

    print(
        f"Over-selection    : {summary['over_selection']}"
    )

    print(
        f"Under-selection   : {summary['under_selection']}"
    )

    print(
        f"Mixed Error       : {summary['mixed_error']}"
    )


    print()
    print(
        f"Exact Accuracy    : {summary['exact_accuracy']:.2%}"
    )

    print(
        f"Precision         : {summary['precision']:.2%}"
    )

    print(
        f"Recall            : {summary['recall']:.2%}"
    )

    print(
        f"F1                : {summary['f1']:.2%}"
    )


    # ========================================================
    # Composition
    # ========================================================

    print()
    print(
        "[Single / Multi Rule]"
    )


    for name, stats in (
        summary[
            "composition"
        ].items()
    ):

        print(
            f"{name:<8} "
            f"| {stats['exact']}/{stats['success']} "
            f"| Accuracy {stats['exact_accuracy']:.2%}"
        )


    # ========================================================
    # Difficulty
    # ========================================================

    print()
    print(
        "[Difficulty]"
    )


    for difficulty, stats in (
        summary[
            "difficulty"
        ].items()
    ):

        print(
            f"{difficulty:<8} "
            f"| Exact {stats['exact']}/{stats['success']} "
            f"| Acc {stats['exact_accuracy']:.2%} "
            f"| P {stats['precision']:.2%} "
            f"| R {stats['recall']:.2%} "
            f"| F1 {stats['f1']:.2%}"
        )


    # ========================================================
    # Rule Performance
    # ========================================================

    print()
    print(
        "[Rule Performance]"
    )


    for rule, stats in (
        summary[
            "rules"
        ].items()
    ):

        if (
            stats[
                "expected_count"
            ] == 0
            and stats[
                "selected_count"
            ] == 0
        ):
            continue


        print(
            f"{rule:<22} "
            f"| Expected {stats['expected_count']:>2} "
            f"| Selected {stats['selected_count']:>2} "
            f"| Correct {stats['correct_count']:>2} "
            f"| Missing {stats['missing_count']:>2} "
            f"| Extra {stats['extra_count']:>2} "
            f"| P {stats['precision']:.2%} "
            f"| R {stats['recall']:.2%}"
        )


    # ========================================================
    # Latency
    # ========================================================

    latency = summary[
        "latency"
    ]


    print()
    print(
        "[Latency]"
    )

    print(
        f"평균 처리 시간    : {latency['average_seconds']:.2f}s"
    )

    print(
        f"최소 처리 시간    : {latency['min_seconds']:.2f}s"
    )

    print(
        f"최대 처리 시간    : {latency['max_seconds']:.2f}s"
    )


# ============================================================
# Main
# ============================================================

def main():

    provider = get_provider()

    result_file = RESULT_FILES[
        provider
    ]


    print(
        f"Provider    : {provider}"
    )

    print(
        f"Result File : {result_file}"
    )


    results = load_results(
        result_file
    )


    summary, details = evaluate(
        provider,
        results,
    )


    summary_file = save_summary(
        provider,
        summary,
    )


    detail_file = save_details(
        provider,
        details,
    )


    print_report(
        provider,
        summary,
    )


    print()
    print(
        "=" * 80
    )

    print(
        "Saved"
    )

    print(
        "=" * 80
    )

    print(
        f"Summary : {summary_file}"
    )

    print(
        f"Details : {detail_file}"
    )


if __name__ == "__main__":
    main()