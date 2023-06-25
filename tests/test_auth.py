import pytest

import server
from tests import TEST_STUDENT_NAME


@pytest.fixture(scope="session")
def app():
    app = server.app
    return app


def test_login(client):
    r = client.post(
        "/login", data={"username": TEST_STUDENT_NAME, "password": "password"}
    )
    assert r.status_code == 302


def test_register(client):
    r = client.post(
        "/register",
        data={
            "school-id": 1,
            "username": "Micheal Jackson",
            "email": "micheal.jackson@whitehouse.gov",
            "role": "student",
            "grade": 9,
            "Create": "on",
        },
    )
    assert r.status_code == 200


def test_logout(client):
    r = client.post("/logout")
    assert r.status_code == 302
