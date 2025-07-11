import pytest
import unittest
from unittest.mock import patch
from app import app
import json

mock_people = {
    "results": [
        {
            "name": "Luke Skywalker",
            "height": "172",
            "mass": "77",
            "gender": "male",
            "skin_color": "fair",
            "hair_color": "blond",
            "eye_color": "blue",
            "birth_year": "19BBY",

        },
        {
            "name": "Leia Organa",
            "height": "150",
            "mass": "49",
            "gender": "female",
            "skin_color": "light",
            "hair_color": "brown",
            "eye_color": "brown",
            "birth_year": "19BBY",
        },
        {
            "name": "Darth Vader",
            "height": "202",
            "mass": "136",
            "gender": "male",
            "skin_color": "white",
            "hair_color": "none",
            "eye_color": "yellow",
            "birth_year": "41.9BBY",
        },
    ]
}


def mock_requests_get(url, verify=False):
    class MockResponse:
        def json(self):
            return mock_people if "?page=1" in url else {"results": []}
    return MockResponse()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('requests.get', side_effect=mock_requests_get)
def test_get_all_people(mock_get, client):
    response = client.get('/people')
    data = response.get_json()

    assert data["status"] == "success"
    assert len(list(data["data"])) == 3

@patch('requests.get', side_effect=mock_requests_get)
def test_filter_by_name(mock_get, client):
    response = client.get('/people?name=luke')
    data = response.get_json()
    
    assert len(list(data["data"])) == 1
    assert data["data"][0]["name"] == "Luke Skywalker"

@patch('requests.get', side_effect=mock_requests_get)
def test_filter_by_gender(mock_get, client):
    response = client.get('/people?gender=female')
    data = response.get_json()

    assert len(list(data["data"])) == 1

@patch('requests.get', side_effect=mock_requests_get)
def test_filter_by_eye_color(mock_get, client):
    response = client.get('/people?eye_color=yellow')
    data = response.get_json()

    assert len(list(data["data"])) == 1

@patch('requests.get', side_effect=mock_requests_get)
def test_filter_by_hair_color(mock_get, client):
    response = client.get('/people?hair_color=brown')
    data = response.get_json()

    assert len(list(data["data"])) == 1

@patch('requests.get', side_effect=mock_requests_get)
def test_filter_by_skin_color(mock_get, client):
    response = client.get('/people?skin_color=white')
    data = response.get_json()

    assert len(list(data["data"])) == 1

@patch('requests.get', side_effect=mock_requests_get)
def test_filter_by_birth_year(mock_get, client):
    response = client.get('/people?birth_year=19BBY')
    data = response.get_json()

    assert len(list(data["data"])) == 2

@patch('requests.get', side_effect=mock_requests_get)
def test_sort_by_name_desc(mock_get, client):
    response = client.get('/people?sort_by=name&sort_dir=desc')
    data = response.get_json()
    names = [p['name'] for p in data["data"]]

    assert names == sorted(names, reverse=True)

@patch('requests.get', side_effect=mock_requests_get)
def test_sort_by_name_asc(mock_get, client):
    response = client.get('/people?sort_by=name&sort_dir=asc')
    data = response.get_json()
    names = [p['name'] for p in data["data"]]

    assert names == sorted(names)

@patch('requests.get', side_effect=mock_requests_get)
def test_empty_result(mock_get, client):
    response = client.get('/people?name=notfound')
    data = response.get_json()

    assert len(data["data"]) == 0

@patch('requests.get', side_effect=mock_requests_get)
def test_invalid_param_type(mock_get, client):
    response = client.get('/people?mass=abc')
    data = response.get_json()

    assert len(data["data"]) == 0  # falha silenciosa

