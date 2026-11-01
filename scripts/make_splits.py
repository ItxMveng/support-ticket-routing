"""Dédoublonne le jeu, le découpe (train / validation / test) et publie ses statistiques.

Usage : uv run python scripts/make_splits.py   (après scripts/download_data.py)
Écrit data/splits/{train,validation,test}.txt (identifiants, versionnés) et docs/donnees.md.
"""

from collections import Counter
from pathlib import Path

from support_ticket_routing.data import (
    FRACTIONS,
    REVISION,
    SEED,
    SPLITS,
    Ticket,
    deduplicate,
    read_tickets,
    select,
    stratified_split,
    write_split,
)

ROOT = Path(__file__).resolve().parents[1]


def table(title: str, parts: dict[str, list[Ticket]], field: str) -> list[str]:
    counts = {name: Counter(getattr(t, field) for t in tickets) for name, tickets in parts.items()}
    total = Counter(getattr(t, field) for tickets in parts.values() for t in tickets)
    lines = [f"### {title}", "", "| " + " | ".join([field, *parts, "total", "part"]) + " |"]
    lines.append("|" + "---|" * (len(parts) + 3))
    n = sum(total.values())
    for value, count in total.most_common():
        cells = [str(counts[name][value]) for name in parts]
        lines.append(
            f"| {value} | " + " | ".join(cells) + f" | {count} | {100 * count / n:.1f} % |"
        )
    return [*lines, ""]


def main() -> None:
    tickets = read_tickets(ROOT / "data" / "raw" / "tickets.csv")
    kept, removed = deduplicate(tickets)
    splits = stratified_split(kept)
    for name in SPLITS:
        write_split(splits[name], ROOT / "data" / "splits" / f"{name}.txt")
    parts = {name: select(kept, splits[name]) for name in SPLITS}
    sizes = ", ".join(f"{name} {len(parts[name])}" for name in SPLITS)
    doc = [
        "# Données",
        "",
        "Généré par `scripts/make_splits.py` : ne pas modifier à la main.",
        "",
        f"- Source : Tobi-Bueck/customer-support-tickets (Hugging Face), révision `{REVISION}`.",
        f"- {len(tickets)} tickets lus, {len(removed)} doublons retirés ({', '.join(removed)}), "
        f"{len(kept)} gardés.",
        f"- Découpage stratifié par (langue, file), graine {SEED}, "
        f"fractions {FRACTIONS} : {sizes}.",
        "",
        *table("Files (catégorie à prédire)", parts, "queue"),
        *table("Priorités", parts, "priority"),
        *table("Langues", parts, "language"),
        *table("Types", parts, "type"),
    ]
    out = ROOT / "docs" / "donnees.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(doc), encoding="utf-8", newline="\n")
    print(sizes)


if __name__ == "__main__":
    main()
