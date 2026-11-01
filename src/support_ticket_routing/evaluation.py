"""Protocole d'évaluation commun : toutes les approches sont notées par ce module, sur le même jeu.

Métriques : F1 macro de la file et de la priorité avec intervalle de confiance (bootstrap),
exactitude, matrices de confusion, latence p50 / p95, coût pour 1 000 tickets, part sans LLM.
"""

import math
import random
from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel

from support_ticket_routing.data import Ticket

BOOTSTRAP_SAMPLES = 1000
BOOTSTRAP_SEED = 2026


class Prediction(BaseModel):
    id: str
    queue: str
    priority: str
    # Confiance sur la file (probabilité de la classe prédite), si l'approche en donne une.
    confidence: float | None = None
    used_llm: bool = False
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


class Classifier(Protocol):
    name: str

    def predict(self, tickets: Sequence[Ticket]) -> list[Prediction]: ...


class Interval(BaseModel):
    value: float
    low: float
    high: float


class Report(BaseModel):
    approche: str
    partie: str
    tickets: int
    f1_macro_file: Interval
    f1_macro_priorite: Interval
    exactitude_file: float
    exactitude_priorite: float
    f1_par_file: dict[str, float]
    confusion_file: dict[str, dict[str, int]]
    confusion_priorite: dict[str, dict[str, int]]
    latence_p50_ms: float
    latence_p95_ms: float
    part_sans_llm: float
    cout_1000_tickets_usd: float


def f1_per_class(
    truth: Sequence[str], predicted: Sequence[str], labels: Sequence[str]
) -> dict[str, float]:
    """F1 de chaque classe ; 0 pour une classe jamais prédite correctement (convention usuelle)."""
    scores: dict[str, float] = {}
    for label in labels:
        tp = sum(t == label and p == label for t, p in zip(truth, predicted, strict=True))
        fp = sum(t != label and p == label for t, p in zip(truth, predicted, strict=True))
        fn = sum(t == label and p != label for t, p in zip(truth, predicted, strict=True))
        scores[label] = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
    return scores


def f1_macro(truth: Sequence[str], predicted: Sequence[str], labels: Sequence[str]) -> float:
    """Moyenne non pondérée des F1 : chaque classe compte autant, même rare."""
    scores = f1_per_class(truth, predicted, labels)
    return sum(scores.values()) / len(scores)


def bootstrap_f1_macro(
    truth: Sequence[str],
    predicted: Sequence[str],
    labels: Sequence[str],
    samples: int = BOOTSTRAP_SAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> Interval:
    """IC à 95 % : tirage des tickets avec remise, percentiles 2,5 et 97,5 du F1 macro."""
    rng = random.Random(seed)
    n = len(truth)
    values = []
    for _ in range(samples):
        idx = [rng.randrange(n) for _ in range(n)]
        values.append(f1_macro([truth[i] for i in idx], [predicted[i] for i in idx], labels))
    return Interval(
        value=f1_macro(truth, predicted, labels),
        low=percentile(values, 0.025),
        high=percentile(values, 0.975),
    )


def confusion(
    truth: Sequence[str], predicted: Sequence[str], labels: Sequence[str]
) -> dict[str, dict[str, int]]:
    """matrice[vraie classe][classe prédite] = nombre de tickets."""
    matrix = {t: dict.fromkeys(labels, 0) for t in labels}
    for t, p in zip(truth, predicted, strict=True):
        matrix[t][p] = matrix[t].get(p, 0) + 1
    return matrix


def percentile(values: Sequence[float], q: float) -> float:
    """Percentile par interpolation linéaire (même convention que numpy par défaut)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower, upper = math.floor(position), math.ceil(position)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def accuracy(truth: Sequence[str], predicted: Sequence[str]) -> float:
    return sum(t == p for t, p in zip(truth, predicted, strict=True)) / len(truth)


def evaluate(
    approach: str,
    split: str,
    tickets: Sequence[Ticket],
    predictions: Sequence[Prediction],
    price_in_per_m: float = 0.0,
    price_out_per_m: float = 0.0,
    samples: int = BOOTSTRAP_SAMPLES,
) -> Report:
    """Note des prédictions. Le coût ne compte que les jetons LLM (tarif public du fournisseur) :
    le calcul CPU des modèles légers est négligé, et le rapport l'indique."""
    by_id = {p.id: p for p in predictions}
    missing = [t.id for t in tickets if t.id not in by_id]
    if missing:
        raise ValueError(f"{len(missing)} tickets sans prédiction, par exemple {missing[:3]}")
    preds = [by_id[t.id] for t in tickets]
    queues = sorted({t.queue for t in tickets})
    priorities = sorted({t.priority for t in tickets})
    true_q, pred_q = [t.queue for t in tickets], [p.queue for p in preds]
    true_p, pred_p = [t.priority for t in tickets], [p.priority for p in preds]
    n = len(tickets)
    tokens_in = sum(p.input_tokens for p in preds) / n
    tokens_out = sum(p.output_tokens for p in preds) / n
    return Report(
        approche=approach,
        partie=split,
        tickets=n,
        f1_macro_file=bootstrap_f1_macro(true_q, pred_q, queues, samples),
        f1_macro_priorite=bootstrap_f1_macro(true_p, pred_p, priorities, samples),
        exactitude_file=accuracy(true_q, pred_q),
        exactitude_priorite=accuracy(true_p, pred_p),
        f1_par_file=f1_per_class(true_q, pred_q, queues),
        confusion_file=confusion(true_q, pred_q, queues),
        confusion_priorite=confusion(true_p, pred_p, priorities),
        latence_p50_ms=percentile([p.latency_ms for p in preds], 0.50),
        latence_p95_ms=percentile([p.latency_ms for p in preds], 0.95),
        part_sans_llm=sum(not p.used_llm for p in preds) / n,
        cout_1000_tickets_usd=1000
        * (tokens_in * price_in_per_m + tokens_out * price_out_per_m)
        / 1e6,
    )


class MajorityClassifier:
    """Référence triviale : prédit toujours la file et la priorité les plus fréquentes de
    l'entraînement. Toute approche doit faire nettement mieux ; elle valide aussi la chaîne."""

    name = "majorite"

    def __init__(self, train: Sequence[Ticket]) -> None:
        self.queue = max(sorted({t.queue for t in train}), key=[t.queue for t in train].count)
        self.priority = max(
            sorted({t.priority for t in train}), key=[t.priority for t in train].count
        )

    def predict(self, tickets: Sequence[Ticket]) -> list[Prediction]:
        return [
            Prediction(id=t.id, queue=self.queue, priority=self.priority, confidence=None)
            for t in tickets
        ]
