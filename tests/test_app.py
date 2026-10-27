"""Normal behaviour of the practice app. No exploit tests here: exploits run only in the sandbox."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from app import CANARY, create_app
from flask.testing import FlaskClient


@pytest.fixture
def client(tmp_path: Path) -> Iterator[FlaskClient]:
    app = create_app(database=tmp_path / "test.db")
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_users(client: FlaskClient) -> None:
    response = client.get("/users")

    assert response.status_code == 200
    assert [u["username"] for u in response.get_json()] == ["alice", "bob", "carol"]


def test_get_user_by_id(client: FlaskClient) -> None:
    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "username": "alice", "email": "alice@example.test"}


def test_unknown_user_is_404(client: FlaskClient) -> None:
    response = client.get("/users/99")

    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}


def test_search_finds_matching_users(client: FlaskClient) -> None:
    response = client.get("/search", query_string={"q": "ali"})

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "username": "alice"}]


def test_search_partial_match_returns_several(client: FlaskClient) -> None:
    response = client.get("/search", query_string={"q": "o"})

    assert [u["username"] for u in response.get_json()] == ["bob", "carol"]


def test_search_without_match_is_empty(client: FlaskClient) -> None:
    response = client.get("/search", query_string={"q": "zed"})

    assert response.status_code == 200
    assert response.get_json() == []


def test_search_without_query_lists_everyone(client: FlaskClient) -> None:
    response = client.get("/search")

    assert [u["username"] for u in response.get_json()] == ["alice", "bob", "carol"]


@pytest.mark.parametrize(
    ("path", "query"),
    [
        ("/health", {}),
        ("/users", {}),
        ("/users/1", {}),
        ("/search", {"q": "a"}),
        ("/search", {}),
    ],
)
def test_normal_responses_never_contain_the_canary(
    client: FlaskClient, path: str, query: dict[str, str]
) -> None:
    response = client.get(path, query_string=query)

    assert CANARY not in response.get_data(as_text=True)
