"""Jeu de tickets : lecture, dédoublonnage et découpage train / validation / test figé.

Source : Tobi-Bueck/customer-support-tickets (Hugging Face), révision et fichier fixés ci-dessous,
vérifiés par empreinte SHA-256. Les données ne sont jamais versionnées ; seuls les identifiants du
découpage le sont (data/splits/), ce qui rend chaque mesure reproductible.
"""

import csv
import random
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path

from pydantic import BaseModel

DATASET_REPO = "Tobi-Bueck/customer-support-tickets"
REVISION = "ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb"
FILENAME = "aa_dataset-tickets-multi-lang-5-2-50-version.csv"
SHA256 = "f187c090e59581c2bbf3aa1377c8db4dd647464ecf2ae51bf8966e42e0ed6bc0"
DOWNLOAD_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/{REVISION}/{FILENAME}"

SPLITS = ("train", "validation", "test")
FRACTIONS = (0.70, 0.15, 0.15)
SEED = 2026


class Ticket(BaseModel):
    id: str
    subject: str
    body: str
    answer: str
    queue: str
    priority: str
    type: str
    language: str

    @property
    def text(self) -> str:
        """Texte présenté aux modèles : sujet (souvent vide) puis corps du message."""
        return f"{self.subject}\n{self.body}".strip()


def ticket_id(index: int) -> str:
    """Identifiant stable : rang de la ligne dans le fichier de la révision fixée."""
    return f"t{index:05d}"


def _clean(value: str) -> str:
    """Fins de ligne unifiées (CRLF → LF) et espaces de bord retirés."""
    return value.replace("\r\n", "\n").strip()


def read_tickets(path: Path) -> list[Ticket]:
    csv.field_size_limit(10**8)
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            Ticket(
                id=ticket_id(index),
                subject=_clean(row["subject"]),
                body=_clean(row["body"]),
                answer=_clean(row["answer"]),
                queue=_clean(row["queue"]),
                priority=_clean(row["priority"]),
                type=_clean(row["type"]),
                language=_clean(row["language"]),
            )
            for index, row in enumerate(csv.DictReader(handle))
        ]


def deduplicate(tickets: Iterable[Ticket]) -> tuple[list[Ticket], list[str]]:
    """Retire les tickets dont le corps a déjà été vu : un doublon de part et d'autre du
    découpage ferait mesurer de la mémorisation. Renvoie les tickets gardés et les retirés."""
    seen: set[str] = set()
    kept: list[Ticket] = []
    removed: list[str] = []
    for ticket in tickets:
        key = " ".join(ticket.body.lower().split())
        if key in seen:
            removed.append(ticket.id)
        else:
            seen.add(key)
            kept.append(ticket)
    return kept, removed


def stratified_split(
    tickets: Sequence[Ticket],
    fractions: Sequence[float] = FRACTIONS,
    seed: int = SEED,
) -> dict[str, list[str]]:
    """Découpe par strate (langue, file) pour garder les mêmes proportions dans chaque partie.

    Déterministe : mêmes tickets et même graine → mêmes identifiants, quel que soit l'ordre
    d'entrée. Le reste des arrondis va à l'entraînement.
    """
    if len(fractions) != len(SPLITS) or abs(sum(fractions) - 1) > 1e-9:
        raise ValueError("il faut trois fractions de somme 1")
    strata: dict[tuple[str, str], list[str]] = defaultdict(list)
    for ticket in tickets:
        strata[(ticket.language, ticket.queue)].append(ticket.id)
    rng = random.Random(seed)
    result: dict[str, list[str]] = {name: [] for name in SPLITS}
    for key in sorted(strata):
        ids = sorted(strata[key])
        rng.shuffle(ids)
        n_validation = round(len(ids) * fractions[1])
        n_test = round(len(ids) * fractions[2])
        result["test"].extend(ids[:n_test])
        result["validation"].extend(ids[n_test : n_test + n_validation])
        result["train"].extend(ids[n_test + n_validation :])
    return {name: sorted(ids) for name, ids in result.items()}


def write_split(ids: Iterable[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{i}\n" for i in ids), encoding="utf-8", newline="\n")


def read_split(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def select(tickets: Iterable[Ticket], ids: Iterable[str]) -> list[Ticket]:
    """Tickets d'une partie du découpage, dans l'ordre des identifiants."""
    by_id = {ticket.id: ticket for ticket in tickets}
    return [by_id[i] for i in ids]
