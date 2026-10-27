"""Small shop API backed by SQLite: users, orders and a product catalog."""

import os
import tempfile
from pathlib import Path

from catalog import catalog
from db import close_db, get_db, init_db
from flask import Flask, Response, jsonify, request


def default_database() -> Path:
    return Path(os.environ.get("APP_DATABASE", Path(tempfile.gettempdir()) / "flask-sqli-multi.db"))


def create_app(database: Path | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = database or default_database()
    init_db(app.config["DATABASE"])
    app.teardown_appcontext(close_db)
    app.register_blueprint(catalog)

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.get("/search")
    def search() -> Response:
        term = request.args.get("q", "")
        sql = "SELECT id, username FROM users WHERE username LIKE ? ORDER BY id"
        rows = get_db().execute(sql, (f"%{term}%",)).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/users/lookup")
    def lookup_user() -> tuple[Response, int]:
        email = request.args.get("email", "")
        row = (
            get_db().execute("SELECT id, username FROM users WHERE email = ?", (email,)).fetchone()
        )
        if row is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row)), 200

    @app.get("/orders")
    def list_orders() -> Response:
        status = request.args.get("status", "open")
        sql = "SELECT id, item FROM orders WHERE status = ? ORDER BY id"
        rows = get_db().execute(sql, (status,)).fetchall()
        return jsonify([dict(row) for row in rows])

    return app


if __name__ == "__main__":
    create_app().run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
