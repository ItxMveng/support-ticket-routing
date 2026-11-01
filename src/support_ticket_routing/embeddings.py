"""Approche 2 : embeddings multilingues (fastembed, local, sans clé) + régression logistique.

Le modèle d'embeddings est gelé : seule la régression logistique est entraînée, une pour la file
et une pour la priorité. Les vecteurs sont normalisés (norme 1) avant la régression.
"""

import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray
from sklearn.linear_model import LogisticRegression

from support_ticket_routing.data import Ticket
from support_ticket_routing.evaluation import Prediction

# Choisi sur la validation (eval/results/embeddings-reglage.json).
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

Vectors = NDArray[np.float32]


class Embedder(Protocol):
    name: str

    def embed(self, texts: Sequence[str]) -> Vectors: ...


class FastEmbedEmbedder:
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        from fastembed import TextEmbedding  # import tardif : les tests n'en ont pas besoin

        self.name = model
        self._model = TextEmbedding(model)

    def embed(self, texts: Sequence[str]) -> Vectors:
        return np.asarray(list(self._model.embed(list(texts))), dtype=np.float32)


def cache_file(directory: Path, model: str, partie: str) -> Path:
    """Fichier de cache des vecteurs d'une partie du découpage (scripts/embed_splits.py)."""
    return directory / f"{model.replace('/', '__')}-{partie}.npy"


def normalize(vectors: Vectors) -> Vectors:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    result: Vectors = (vectors / np.maximum(norms, 1e-12)).astype(np.float32)
    return result


@dataclass(frozen=True)
class EmbeddingSettings:
    c: float = 256.0  # choisi sur la validation (eval/results/embeddings-reglage.json)
    class_weight: str | None = None


def fit_logistic(vectors: Vectors, labels: Sequence[str], settings: EmbeddingSettings) -> Any:
    return LogisticRegression(
        C=settings.c, class_weight=settings.class_weight, max_iter=3000, random_state=0
    ).fit(vectors, list(labels))


class EmbeddingClassifier:
    name = "embeddings"

    def __init__(
        self,
        train: Sequence[Ticket],
        embedder: Embedder | None = None,
        settings: EmbeddingSettings | None = None,
        train_vectors: Vectors | None = None,
    ) -> None:
        """`train_vectors` évite de recalculer les vecteurs déjà en cache (scripts)."""
        self.embedder = embedder or FastEmbedEmbedder()
        self.settings = settings or EmbeddingSettings()
        if train_vectors is None:
            train_vectors = self.embedder.embed([t.text for t in train])
        vectors = normalize(train_vectors)
        self.queue_model = fit_logistic(vectors, [t.queue for t in train], self.settings)
        self.priority_model = fit_logistic(vectors, [t.priority for t in train], self.settings)

    def predict(self, tickets: Sequence[Ticket]) -> list[Prediction]:
        """Ticket par ticket, embedding compris : la latence est celle d'une requête de l'API."""
        predictions = []
        for ticket in tickets:
            start = time.perf_counter()
            vector = normalize(self.embedder.embed([ticket.text]))
            queue_proba = self.queue_model.predict_proba(vector)[0]
            priority = str(self.priority_model.predict(vector)[0])
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
