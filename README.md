Deliberately vulnerable. For local testing of Vulcan only. Never deploy.

# flask-sqli

A small Flask user directory API backed by SQLite. It is a Vulcan benchmark target: it contains
one deliberate vulnerability, reported in `report.sarif`. All data is fake, and the `secrets`
table holds only a harmless canary value.

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

| Route | Description |
|---|---|
| `GET /health` | Health check |
| `GET /users` | List users |
| `GET /users/<id>` | One user, or 404 |
| `GET /search?q=<text>` | Users whose name contains the text |
