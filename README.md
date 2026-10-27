Deliberately vulnerable. For local testing of Vulcan only. Never deploy.

# flask-sqli-multi

A small Flask shop API backed by SQLite. It is a Vulcan benchmark target for category-level
fixing (T-4.8): it contains three deliberate SQL injections in three routes, two of them in the
same file, reported in `report.sarif`. `/users/lookup` is a safe control (parameterised query).
All data is fake, and the `secrets` table holds only a harmless canary value.

## Run

```
pip install -r requirements.txt
python app.py
```

The app listens on `http://127.0.0.1:5000`. Set `HOST` and `PORT` to change this, and
`APP_DATABASE` to choose the SQLite file (default: a file in the system temp directory).

## Test

```
pytest
```

## Routes

| Route | Description | Finding |
|---|---|---|
| `GET /health` | Health check | |
| `GET /search?q=<text>` | Users whose name contains the text | 101-1 (`app.py`) |
| `GET /users/lookup?email=<email>` | One user by email, or 404 (safe control) | |
| `GET /orders?status=<status>` | Orders with that status (default `open`) | 101-2 (`app.py`) |
| `GET /products?category=<name>` | Products in that category (default `office`) | 101-3 (`catalog.py`) |

`patches/` holds fixed patches for the integration tests (see `patches/README.md`).
