"""Product catalog routes."""

from db import get_db
from flask import Blueprint, Response, jsonify, request

catalog = Blueprint("catalog", __name__)


@catalog.get("/products")
def list_products() -> Response:
    category = request.args.get("category", "office")
    sql = f"SELECT id, name FROM products WHERE category = '{category}' ORDER BY id"
    rows = get_db().execute(sql).fetchall()
    return jsonify([dict(row) for row in rows])
