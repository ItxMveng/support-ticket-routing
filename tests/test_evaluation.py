import pytest

from support_ticket_routing.data import Ticket
from support_ticket_routing.evaluation import (
    MajorityClassifier,
    Prediction,
    bootstrap_f1_macro,
    confusion,
    evaluate,
    f1_macro,
    f1_per_class,
    percentile,
)


def _ticket(i: int, queue: str, priority: str = "low") -> Ticket:
    return Ticket(
        id=f"t{i}",
        subject="",
        body=f"m{i}",
        answer="",
        queue=queue,
        priority=priority,
        type="Incident",
        language="en",
    )


def test_f1_per_class_matches_hand_computation() -> None:
    truth = ["a", "a", "a", "b"]
    predicted = ["a", "a", "b", "b"]
    # a : tp 2, fp 0, fn 1 → 4/5 ; b : tp 1, fp 1, fn 0 → 2/3
    scores = f1_per_class(truth, predicted, ["a", "b"])
    assert scores == pytest.approx({"a": 0.8, "b": 2 / 3})
    assert f1_macro(truth, predicted, ["a", "b"]) == pytest.approx((0.8 + 2 / 3) / 2)


def test_class_never_predicted_counts_zero_in_the_macro() -> None:
    # Prédire toujours la classe majoritaire : bonne exactitude, mauvais F1 macro.
    truth = ["a"] * 9 + ["b"]
    assert f1_macro(truth, ["a"] * 10, ["a", "b"]) == pytest.approx((18 / 19 + 0) / 2)


def test_bootstrap_interval_contains_value_and_is_reproducible() -> None:
    truth = ["a", "b", "c"] * 20
    predicted = ["a", "b", "b"] * 20
    first = bootstrap_f1_macro(truth, predicted, ["a", "b", "c"], samples=200)
    assert first.low <= first.value <= first.high
    assert first == bootstrap_f1_macro(truth, predicted, ["a", "b", "c"], samples=200)


def test_confusion_rows_are_true_labels() -> None:
    matrix = confusion(["a", "a", "b"], ["a", "b", "b"], ["a", "b"])
    assert matrix == {"a": {"a": 1, "b": 1}, "b": {"a": 0, "b": 1}}


def test_percentile_interpolates_like_numpy() -> None:
    assert percentile([1, 2, 3, 4], 0.5) == 2.5
    assert percentile([10, 20, 30, 40, 50], 0.95) == pytest.approx(48)
    assert percentile([], 0.5) == 0.0


def test_evaluate_reports_cost_latency_and_share_without_llm() -> None:
    tickets = [_ticket(1, "a", "low"), _ticket(2, "b", "high")]
    predictions = [
        Prediction(id="t1", queue="a", priority="low", latency_ms=2),
        Prediction(
            id="t2",
            queue="a",
            priority="high",
            used_llm=True,
            latency_ms=900,
            input_tokens=1000,
            output_tokens=100,
        ),
    ]
    report = evaluate("test", "validation", tickets, predictions, 0.15, 0.60, samples=50)
    assert report.exactitude_file == 0.5 and report.exactitude_priorite == 1.0
    assert report.part_sans_llm == 0.5
    # par ticket : 500 jetons en entrée et 50 en sortie → 1 000 tickets = 0,5 M et 0,05 M
    assert report.cout_1000_tickets_usd == pytest.approx(0.5 * 0.15 + 0.05 * 0.60)
    assert report.latence_p50_ms == pytest.approx(451)


def test_evaluate_refuses_missing_predictions() -> None:
    with pytest.raises(ValueError, match="sans prédiction"):
        evaluate("test", "validation", [_ticket(1, "a")], [])


def test_majority_classifier_predicts_most_frequent_labels() -> None:
    train = [_ticket(1, "a", "low"), _ticket(2, "b", "high"), _ticket(3, "b", "high")]
    predictions = MajorityClassifier(train).predict([_ticket(9, "a")])
    assert (predictions[0].queue, predictions[0].priority) == ("b", "high")
