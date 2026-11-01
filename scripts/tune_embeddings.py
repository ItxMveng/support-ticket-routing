"""Choisit le modèle d'embeddings et les réglages de la régression sur la VALIDATION.

Usage : uv run python scripts/tune_embeddings.py <modèle> [<modèle> ...]
Prérequis : scripts/embed_splits.py <modèle> (cache des vecteurs).
Écrit eval/results/embeddings-reglage.json. Critère : moyenne des F1 macro file et priorité,
comme pour TF-IDF (tune_tfidf.py).
"""

import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np

from support_ticket_routing.data import read_split, read_tickets, select
from support_ticket_routing.embeddings import (
    EmbeddingSettings,
    cache_file,
    fit_logistic,
    normalize,
)
from support_ticket_routing.evaluation import f1_macro

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "processed" / "embeddings"
C_GRID = [1.0, 4.0, 16.0, 64.0, 256.0, 1024.0]
WEIGHT_GRID: list[str | None] = [None, "balanced"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("modeles", nargs="+")
    args = parser.parse_args()
    tickets = read_tickets(ROOT / "data" / "raw" / "tickets.csv")
    train = select(tickets, read_split(ROOT / "data" / "splits" / "train.txt"))
    valid = select(tickets, read_split(ROOT / "data" / "splits" / "validation.txt"))
    rows = []
    for model in args.modeles:
        x_train = normalize(np.load(cache_file(CACHE, model, "train")))
        x_valid = normalize(np.load(cache_file(CACHE, model, "validation")))
        for c, weight in itertools.product(C_GRID, WEIGHT_GRID):
            settings = EmbeddingSettings(c=c, class_weight=weight)
            start = time.perf_counter()
            scores = {}
            for field in ("queue", "priority"):
                fitted = fit_logistic(x_train, [getattr(t, field) for t in train], settings)
                predicted = [str(p) for p in fitted.predict(x_valid)]
                truth = [getattr(t, field) for t in valid]
                scores[field] = f1_macro(truth, predicted, sorted(set(truth)))
            row = {
                "modele": model,
                "dimension": int(x_train.shape[1]),
                "c": c,
                "class_weight": weight,
                "f1_macro_file": round(scores["queue"], 4),
                "f1_macro_priorite": round(scores["priority"], 4),
                "critere": round((scores["queue"] + scores["priority"]) / 2, 4),
                "secondes": round(time.perf_counter() - start, 1),
            }
            rows.append(row)
            print(json.dumps(row), flush=True)
    best = max(rows, key=lambda r: r["critere"])
    out = ROOT / "eval" / "results" / "embeddings-reglage.json"
    out.write_text(
        json.dumps({"partie": "validation", "grille": rows, "retenu": best}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("retenu :", best)


if __name__ == "__main__":
    main()
