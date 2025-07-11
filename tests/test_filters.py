import pytest
from unittest.mock import patch
from app import app

mock_data = {
    "people": {
        "results": [
            {"name": "Luke Skywalker", "gender": "male", "eye_color": "blue", "birth_year": "19BBY", "hair_color": "blond", "skin_color": "fair"},
            {"name": "Leia Organa", "gender": "female", "eye_color": "brown", "birth_year": "19BBY", "hair_color": "brown", "skin_color": "light"},
            {"name": "Darth Vader", "gender": "male", "eye_color": "yellow", "birth_year": "41.9BBY", "hair_color": "none", "skin_color": "white"},
        ]
    },
    "films": {
        "results": [
            {"title": "A New Hope", "episode_id": 4, "director": "George Lucas"},
            {"title": "The Empire Strikes Back", "episode_id": 5, "director": "Irvin Kershner"},
        ]
    },
    "species": {
        "results": [
            {"name": "Human", "language": "Galactic Basic", "classification": "mammal"},
            {"name": "Wookiee", "language": "Shyriiwook", "classification": "mammal"},
        ]
    },
    "planets": {
        "results": [
            {"name": "Tatooine", "climate": "arid", "terrain": "desert"},
            {"name": "Hoth", "climate": "frozen", "terrain": "tundra, ice caves"},
        ]
    },
    "starships": {
        "results": [
            {"name": "Millennium Falcon", "model": "YT-1300 light freighter", "manufacturer": "Corellian Engineering Corporation"},
            {"name": "X-wing", "model": "T-65 X-wing", "manufacturer": "Incom Corporation"},
        ]
    },
    "vehicles": {
        "results": [
            {"name": "Sand Crawler", "model": "Digger Crawler", "manufacturer": "Corellia Mining Corporation"},
            {"name": "TIE/LN starfighter", "model": "Twin Ion Engine", "manufacturer": "Sienar Fleet Systems"},
        ]
    },
}

def generate_mock_get(resource_name):
    def _mock_requests_get(url, verify=False):
        class MockResponse:
            def json(self):
                if f"/{resource_name}" in url and "?page=1" in url:
                    return mock_data[resource_name]
                return {"results": []}
        return MockResponse()
    return _mock_requests_get

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("resource,query,expected_count,expected_field,expected_value", [

    ("people", "name=luke", 1, "name", "Luke Skywalker"),
    ("people", "gender=male", 2, "gender", "male"),
    ("people", "eye_color=yellow", 1, "eye_color", "yellow"),
    ("people", "birth_year=19BBY", 2, "birth_year", "19bby"),
   
    ("films", "director=George Lucas", 1, "director", "George Lucas"),
    ("films", "episode_id=5", 1, "episode_id", 5),
    
    ("species", "language=Galactic Basic", 1, "language", "galactic basic"),
    ("species", "classification=mammal", 2, "classification", "mammal"),

    ("planets", "climate=arid", 1, "climate", "arid"),
    ("planets", "terrain=desert", 1, "terrain", "desert"),

    ("starships", "model=YT-1300 light freighter", 1, "model", "yt-1300 light freighter"),
    ("starships", "manufacturer=Incom Corporation", 1, "manufacturer", "incom corporation"),

    ("vehicles", "name=Sand Crawler", 1, "name", "sand crawler"),
    ("vehicles", "manufacturer=Sienar Fleet Systems", 1, "manufacturer", "sienar fleet systems"),
])
def test_resource_filters(resource, query, expected_count, expected_field, expected_value, client):
    mock_func = generate_mock_get(resource)

    with patch('requests.get', side_effect=mock_func):
        response = client.get(f"/{resource}?{query}")
        data = response.get_json()

        assert response.status_code == 200
        assert data["status"] == "success"
        assert len(data["data"]) == expected_count

        for item in data["data"]:
            value = str(item.get(expected_field, "")).lower()
            expected = str(expected_value).lower()
            assert expected in value
