"""API de classification des tickets (squelette : seule la route de santé existe au kickoff)."""

from fastapi import FastAPI
from pydantic import BaseModel

from support_ticket_routing import __version__

app = FastAPI(title="Routage des tickets de support", version=__version__)


class Health(BaseModel):
    status: str
    version: str


@app.get("/health")
def health() -> Health:
    return Health(status="ok", version=__version__)
