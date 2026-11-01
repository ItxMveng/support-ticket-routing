"""Note une approche sur une partie du découpage, avec le protocole commun.

Usage : uv run python scripts/evaluate.py <approche> [--partie validation|test]
Écrit eval/results/<approche>-<partie>.json (rapport) et -predictions.jsonl (une ligne par ticket).
Approches disponibles : voir APPROCHES (chaque ticket P2-03 à P2-08 en ajoute une).
"""

import argparse
import json
from collections.abc import Callable, Sequence
from pathlib import Path

from support_ticket_routing.data import Ticket, read_split, read_tickets, select
from support_ticket_routing.evaluation import Classifier, MajorityClassifier, evaluate
from support_ticket_routing.tfidf import TfidfClassifier

ROOT = Path(__file__).resolve().parents[1]
APPROCHES: dict[str, Callable[[Sequence[Ticket]], Classifier]] = {
    "majorite": MajorityClassifier,
    "tfidf": TfidfClassifier,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("approche", choices=sorted(APPROCHES))
    parser.add_argument("--partie", choices=["validation", "test"], default="validation")
    args = parser.parse_args()

    tickets = read_tickets(ROOT / "data" / "raw" / "tickets.csv")
    train = select(tickets, read_split(ROOT / "data" / "splits" / "train.txt"))
    part = select(tickets, read_split(ROOT / "data" / "splits" / f"{args.partie}.txt"))
    classifier = APPROCHES[args.approche](train)
    predictions = classifier.predict(part)
    report = evaluate(args.approche, args.partie, part, predictions)

    out = ROOT / "eval" / "results"
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{args.approche}-{args.partie}"
    (out / f"{stem}.json").write_text(
        report.model_dump_json(indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    with (out / f"{stem}-predictions.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for prediction in predictions:
            handle.write(prediction.model_dump_json() + "\n")
    f1q, f1p = report.f1_macro_file, report.f1_macro_priorite
    print(
        json.dumps(
            {
                "approche": report.approche,
                "partie": report.partie,
                "tickets": report.tickets,
                "f1_macro_file": [round(f1q.value, 3), round(f1q.low, 3), round(f1q.high, 3)],
                "f1_macro_priorite": [round(f1p.value, 3), round(f1p.low, 3), round(f1p.high, 3)],
                "exactitude_file": round(report.exactitude_file, 3),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
