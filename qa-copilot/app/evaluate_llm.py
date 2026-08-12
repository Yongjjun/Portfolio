from llm_analyzer import analyze_requirement
from evaluate_rules import TEST_DATASET


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


def evaluate_llm():
    results = []

    for case in TEST_DATASET:
        print(f"\n[{case['id']}]")
        print(f"Requirement : {case['requirement']}")
        print(f"Expected    : {case['expected']}")

        try:
            result = analyze_requirement(case["requirement"])
            actual = [item["rule"] for item in result]

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

        except Exception as e:
            print(f"ERROR: {e}")

    if results:
        avg_precision = sum(
            result["precision"] for result in results
        ) / len(results)

        avg_recall = sum(
            result["recall"] for result in results
        ) / len(results)

        avg_f1 = sum(
            result["f1"] for result in results
        ) / len(results)

        exact_matches = sum(
            result["exact_match"] for result in results
        )

        print("\n" + "=" * 80)
        print("Gemini Evaluation Summary")
        print("=" * 80)

        print(f"Total Cases     : {len(results)}")
        print(f"Exact Match     : {exact_matches}/{len(results)}")
        print(f"Exact Match     : {exact_matches / len(results):.2%}")
        print(f"Average Precision: {avg_precision:.2%}")
        print(f"Average Recall   : {avg_recall:.2%}")
        print(f"Average F1 Score : {avg_f1:.2%}")


if __name__ == "__main__":
    evaluate_llm()