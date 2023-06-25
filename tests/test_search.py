import pytest

import server


@pytest.fixture(scope="session")
def app():
    app = server.app
    return app


def test_api_suggest(client):
    r = client.get("/api/suggest.json?q=adam")
    assert r.status_code == 200


def test_api_students_empty(client):
    r = client.get("/api/students.json")
    assert r.status_code == 200


def test_api_students_grade_filter(client):
    r = client.get("/api/students.json?show_9th=false")
    assert r.status_code == 200


def test_api_students_query(client):
    r = client.get("/api/students.json?q=adam")
    assert r.status_code == 200


def test_api_students_sort(client):
    r = client.get("/api/students.json?sort=name_asc")
    assert r.status_code == 200

def test_api_students_score_condition(client):
    r = client.get("/api/students.json?scorecondition=>3000")
    assert r.status_code == 200
