import pytest

import server
from tests import TEST_ADMIN_NAME, TEST_STUDENT_NAME


@pytest.fixture(scope="session")
def app():
    app = server.app
    return app


def test_student_api_events(client):
    with client.session_transaction() as session:
        session["username"] = TEST_STUDENT_NAME
        session["role"] = "STUDENT"
    r = client.get("/api/events.json")
    assert r.status_code == 200

def test_admin_api_events(client):
    with client.session_transaction() as session:
        session["username"] = TEST_ADMIN_NAME
        session["role"] = "ADMINISTRATOR"
    r = client.get("/api/events.json")
    assert r.status_code == 200