"""Choisit les réglages TF-IDF + régression logistique sur la VALIDATION (jamais sur le test).

Usage : uv run python scripts/tune_tfidf.py   → eval/results/tfidf-reglage.json
Critère : moyenne des F1 macro de la file et de la priorité.
"""

import itertools
import json
import time
from pathlib import Path

from support_ticket_routing.data import read_split, read_tickets, select
from support_ticket_routing.evaluation import f1_macro
from support_ticket_routing.tfidf import TfidfSettings, _pipeline

ROOT = Path(__file__).resolve().parents[1]
GRID = {"c": [1.0, 4.0, 16.0, 64.0, 256.0], "class_weight": [None, "balanced"]}


def main() -> None:
    tickets = read_tickets(ROOT / "data" / "raw" / "tickets.csv")
    train = select(tickets, read_split(ROOT / "data" / "splits" / "train.txt"))
    valid = select(tickets, read_split(ROOT / "data" / "splits" / "validation.txt"))
    texts = [t.text for t in train]
    rows = []
    for c, weight in itertools.product(GRID["c"], GRID["class_weight"]):
        settings = TfidfSettings(c=c, class_weight=weight)
        start = time.perf_counter()
        scores = {}
        for field in ("queue", "priority"):
            model = _pipeline(settings).fit(texts, [getattr(t, field) for t in train])
            predicted = [str(p) for p in model.predict([t.text for t in valid])]
            truth = [getattr(t, field) for t in valid]
            scores[field] = f1_macro(truth, predicted, sorted(set(truth)))
        row = {
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
    out = ROOT / "eval" / "results" / "tfidf-reglage.json"
    out.write_text(
        json.dumps({"partie": "validation", "grille": rows, "retenu": best}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("retenu :", best)


if __name__ == "__main__":
    main()
