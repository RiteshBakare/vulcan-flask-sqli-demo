"""Database setup and per-request connections. All data is fake."""

import sqlite3
from pathlib import Path

from flask import current_app, g

CANARY = "VULCAN-CANARY-5f1c9a2e7b3d"

SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS secrets;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    item TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);
CREATE TABLE secrets (
    name TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

USERS = [
    (1, "alice", "alice@example.test"),
    (2, "bob", "bob@example.test"),
    (3, "carol", "carol@example.test"),
]

ORDERS = [
    (1, "lamp", "open"),
    (2, "desk", "shipped"),
    (3, "chair", "open"),
]

PRODUCTS = [
    (1, "pen", "office"),
    (2, "mug", "kitchen"),
    (3, "stapler", "office"),
]


def init_db(database: Path) -> None:
    with sqlite3.connect(database) as conn:
        conn.executescript(SCHEMA)
        conn.executemany("INSERT INTO users (id, username, email) VALUES (?, ?, ?)", USERS)
        conn.executemany("INSERT INTO orders (id, item, status) VALUES (?, ?, ?)", ORDERS)
        conn.executemany("INSERT INTO products (id, name, category) VALUES (?, ?, ?)", PRODUCTS)
        conn.execute("INSERT INTO secrets (name, value) VALUES (?, ?)", ("admin_api_token", CANARY))
    conn.close()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    db: sqlite3.Connection = g.db
    return db


def close_db(_exc: BaseException | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()
