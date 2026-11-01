from fastapi.testclient import TestClient

from support_ticket_routing import __version__
from support_ticket_routing.api import app


def test_health_returns_ok_and_version() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
