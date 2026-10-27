"""Small user directory API backed by SQLite."""

import os
import sqlite3
import tempfile
from pathlib import Path

from flask import Flask, Response, current_app, g, jsonify, request

CANARY = "VULCAN-CANARY-5f1c9a2e7b3d"

SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS secrets;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL
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


def default_database() -> Path:
    return Path(os.environ.get("APP_DATABASE", Path(tempfile.gettempdir()) / "flask-sqli.db"))


def init_db(database: Path) -> None:
    with sqlite3.connect(database) as conn:
        conn.executescript(SCHEMA)
        conn.executemany("INSERT INTO users (id, username, email) VALUES (?, ?, ?)", USERS)
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


def create_app(database: Path | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = database or default_database()
    init_db(app.config["DATABASE"])
    app.teardown_appcontext(close_db)

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.get("/users")
    def list_users() -> Response:
        rows = get_db().execute("SELECT id, username FROM users ORDER BY id").fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/users/<int:user_id>")
    def get_user(user_id: int) -> tuple[Response, int]:
        row = (
            get_db()
            .execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
            .fetchone()
        )
        if row is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row)), 200

    @app.get("/search")
    def search() -> Response:
        term = request.args.get("q", "")
        sql = f"SELECT id, username FROM users WHERE username LIKE '%{term}%' ORDER BY id"
        rows = get_db().execute(sql).fetchall()
        return jsonify([dict(row) for row in rows])

    return app


if __name__ == "__main__":
    create_app().run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
