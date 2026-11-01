"""Télécharge le jeu de tickets à la révision fixée et vérifie son empreinte SHA-256.

Usage : uv run python scripts/download_data.py   → data/raw/tickets.csv (jamais versionné)
"""

import hashlib
import sys
from pathlib import Path

import httpx

from support_ticket_routing.data import DOWNLOAD_URL, SHA256

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "tickets.csv"


def main() -> int:
    if OUT.exists() and hashlib.sha256(OUT.read_bytes()).hexdigest() == SHA256:
        print(f"déjà présent et vérifié : {OUT}")
        return 0
    response = httpx.get(DOWNLOAD_URL, follow_redirects=True, timeout=300)
    response.raise_for_status()
    digest = hashlib.sha256(response.content).hexdigest()
    if digest != SHA256:
        print(f"empreinte inattendue : {digest} (attendue : {SHA256})")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(response.content)
    print(f"{len(response.content) / 1e6:.1f} Mo vérifiés → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
