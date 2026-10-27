"""Normal behaviour of the practice app. No exploit tests here: exploits run only in the sandbox."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from app import create_app
from db import CANARY
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


def test_search_finds_matching_users(client: FlaskClient) -> None:
    response = client.get("/search", query_string={"q": "ali"})

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "username": "alice"}]


def test_search_partial_match_returns_several(client: FlaskClient) -> None:
    response = client.get("/search", query_string={"q": "o"})

    assert [u["username"] for u in response.get_json()] == ["bob", "carol"]


def test_search_without_query_lists_everyone(client: FlaskClient) -> None:
    response = client.get("/search")

    assert [u["username"] for u in response.get_json()] == ["alice", "bob", "carol"]


def test_lookup_finds_user_by_email(client: FlaskClient) -> None:
    response = client.get("/users/lookup", query_string={"email": "bob@example.test"})

    assert response.status_code == 200
    assert response.get_json() == {"id": 2, "username": "bob"}


def test_lookup_unknown_email_is_404(client: FlaskClient) -> None:
    response = client.get("/users/lookup", query_string={"email": "zed@example.test"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}


def test_orders_default_to_open(client: FlaskClient) -> None:
    response = client.get("/orders")

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "item": "lamp"}, {"id": 3, "item": "chair"}]


def test_orders_by_status(client: FlaskClient) -> None:
    response = client.get("/orders", query_string={"status": "shipped"})

    assert response.get_json() == [{"id": 2, "item": "desk"}]


def test_orders_unknown_status_is_empty(client: FlaskClient) -> None:
    response = client.get("/orders", query_string={"status": "lost"})

    assert response.status_code == 200
    assert response.get_json() == []


def test_products_default_to_office(client: FlaskClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "name": "pen"}, {"id": 3, "name": "stapler"}]


def test_products_by_category(client: FlaskClient) -> None:
    response = client.get("/products", query_string={"category": "kitchen"})

    assert response.get_json() == [{"id": 2, "name": "mug"}]


@pytest.mark.parametrize(
    ("path", "query"),
    [
        ("/health", {}),
        ("/search", {"q": "a"}),
        ("/users/lookup", {"email": "alice@example.test"}),
        ("/orders", {}),
        ("/products", {}),
    ],
)
def test_normal_responses_never_contain_the_canary(
    client: FlaskClient, path: str, query: dict[str, str]
) -> None:
    response = client.get(path, query_string=query)

    assert CANARY not in response.get_data(as_text=True)
