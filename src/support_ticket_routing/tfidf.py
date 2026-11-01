"""Base de référence : TF-IDF + régression logistique, un modèle pour la file, un pour la priorité.

Choix courant et solide pour classer du texte court : rapide à entraîner (quelques secondes sur
CPU), sans GPU ni appel externe, et sa probabilité sert de confiance au routage hybride (P2-08).
"""

import time
from collections.abc import Sequence
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline

from support_ticket_routing.data import Ticket
from support_ticket_routing.evaluation import Prediction


@dataclass(frozen=True)
class TfidfSettings:
    # Inverse de la régularisation : plus C est grand, moins le modèle est contraint.
    c: float = 64.0  # choisi sur la validation (eval/results/tfidf-reglage.json)
    # « balanced » compense le déséquilibre des files (de 29 % à 1,4 %) en pondérant les rares.
    class_weight: str | None = "balanced"
    ngram_max: int = 2
    min_df: int = 2


def _pipeline(settings: TfidfSettings) -> Pipeline:
    return make_pipeline(
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, settings.ngram_max),
            min_df=settings.min_df,
            sublinear_tf=True,
        ),
        LogisticRegression(
            C=settings.c, class_weight=settings.class_weight, max_iter=2000, random_state=0
        ),
    )


class TfidfClassifier:
    name = "tfidf"

    def __init__(self, train: Sequence[Ticket], settings: TfidfSettings | None = None) -> None:
        self.settings = settings or TfidfSettings()
        texts = [t.text for t in train]
        self.queue_model = _pipeline(self.settings).fit(texts, [t.queue for t in train])
        self.priority_model = _pipeline(self.settings).fit(texts, [t.priority for t in train])

    def predict(self, tickets: Sequence[Ticket]) -> list[Prediction]:
        """Prédit ticket par ticket : la latence mesurée est celle d'une requête de l'API."""
        predictions = []
        for ticket in tickets:
            start = time.perf_counter()
            queue_proba = self.queue_model.predict_proba([ticket.text])[0]
            priority = str(self.priority_model.predict([ticket.text])[0])
            best = int(queue_proba.argmax())
            predictions.append(
                Prediction(
                    id=ticket.id,
                    queue=str(self.queue_model.classes_[best]),
                    priority=priority,
                    confidence=float(queue_proba[best]),
                    latency_ms=(time.perf_counter() - start) * 1000,
                )
            )
        return predictions
