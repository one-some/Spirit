import pytest
import requests

import server


@pytest.fixture(scope="session")
def app():
    app = server.app
    return app


def test_login(client):
    r = client.post("/login", data={"username": "Isabel Miles", "password": "password"})
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
        },
    )
    assert r.status_code == 200
