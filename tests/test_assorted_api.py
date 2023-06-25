import pytest

import server
from tests import TEST_STUDENT_NAME


@pytest.fixture(scope="session")
def app():
    app = server.app
    return app


def test_api_prizes(client):
    r = client.get("/api/prizes.json")
    assert r.status_code == 200


def test_api_stats(client):
    r = client.get("/api/stats.json")
    assert r.status_code == 200


def test_api_audit_log(client):
    r = client.get("/api/audit_log.json")
    assert r.status_code == 200
