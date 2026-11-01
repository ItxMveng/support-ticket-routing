from collections.abc import Sequence

import numpy as np
import pytest

from support_ticket_routing.data import Ticket
from support_ticket_routing.embeddings import EmbeddingClassifier, Vectors, normalize

# Faux modèle d'embeddings : un axe par mot-clé, pour tester la chaîne sans télécharger de modèle.
KEYWORDS = ["invoice", "refund", "vpn", "server", "urgent"]


class KeywordEmbedder:
    name = "mots-cles"

    def __init__(self) -> None:
        self.calls = 0

    def embed(self, texts: Sequence[str]) -> Vectors:
        self.calls += 1
        return np.asarray(
            [[float(k in t) + 0.01 for k in KEYWORDS] for t in texts], dtype=np.float32
        )


def _ticket(i: int, text: str, queue: str = "?", priority: str = "?") -> Ticket:
    return Ticket(
        id=f"t{i}",
        subject="",
        body=text,
        answer="",
        queue=queue,
        priority=priority,
        type="Incident",
        language="en",
    )


TRAIN = [
    _ticket(i, text, queue, priority)
    for i, (text, queue, priority) in enumerate(
        [
            ("invoice refund", "Billing and Payments", "medium"),
            ("refund invoice please", "Billing and Payments", "medium"),
            ("vpn server urgent", "IT Support", "high"),
            ("server vpn urgent down", "IT Support", "high"),
        ]
        * 3
    )
]


def test_normalize_gives_unit_rows_and_keeps_zero_rows_finite() -> None:
    result = normalize(np.asarray([[3.0, 4.0], [0.0, 0.0]], dtype=np.float32))
    assert result[0] == pytest.approx([0.6, 0.8])
    assert np.isfinite(result).all()


def test_learns_queue_priority_and_confidence() -> None:
    model = EmbeddingClassifier(TRAIN, embedder=KeywordEmbedder())
    [billing, it] = model.predict([_ticket(100, "refund my invoice"), _ticket(101, "vpn down")])
    assert (billing.queue, billing.priority) == ("Billing and Payments", "medium")
    assert (it.queue, it.priority) == ("IT Support", "high")
    assert billing.confidence is not None and 0.5 < billing.confidence <= 1.0
    assert not billing.used_llm and billing.latency_ms >= 0


def test_precomputed_train_vectors_skip_embedding_the_training_set() -> None:
    embedder = KeywordEmbedder()
    vectors = KeywordEmbedder().embed([t.text for t in TRAIN])
    EmbeddingClassifier(TRAIN, embedder=embedder, train_vectors=vectors)
    assert embedder.calls == 0
