"""Calcule et met en cache les embeddings de chaque partie du découpage, pour un modèle donné.

Usage : uv run python scripts/embed_splits.py <modèle fastembed>
Écrit data/processed/embeddings/<modèle>-<partie>.npy (non versionné, recalculable) et affiche
le temps de calcul. Le réglage (tune_embeddings.py) relit ce cache au lieu de recalculer.
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

from support_ticket_routing.data import read_split, read_tickets, select
from support_ticket_routing.embeddings import FastEmbedEmbedder, cache_file

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "processed" / "embeddings"
PARTIES = ("train", "validation", "test")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("modele")
    args = parser.parse_args()
    tickets = read_tickets(ROOT / "data" / "raw" / "tickets.csv")
    embedder = FastEmbedEmbedder(args.modele)
    CACHE.mkdir(parents=True, exist_ok=True)
    for partie in PARTIES:
        part = select(tickets, read_split(ROOT / "data" / "splits" / f"{partie}.txt"))
        start = time.perf_counter()
        vectors = embedder.embed([t.text for t in part])
        seconds = time.perf_counter() - start
        np.save(cache_file(CACHE, args.modele, partie), vectors)
        info = {"modele": args.modele, "partie": partie, "tickets": len(part)}
        print(json.dumps(info | {"secondes": round(seconds, 1)}), flush=True)


if __name__ == "__main__":
    main()
