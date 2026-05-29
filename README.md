# Stock Movement — JLC GROUP 2026

Full-stack stock movement tracker.
**Frontend (HTML/JS) → Flask API → PostgreSQL.**

## Structure

```
stock_movement/
├── .env                  # DB credentials & settings (not committed)
├── .env.example          # template for .env
├── config.py             # loads .env → central paths + DB config
├── requirements.txt
├── server/
│   └── app.py            # Flask API + serves the frontend
├── scripts/              # data pipeline / tooling
│   ├── extract_data.py   # Excel  → data/processed/stock_data.json
│   ├── setup_database.py # JSON   → PostgreSQL (schema + load)
│   ├── verify_data.py    # verify Excel ⇄ PostgreSQL
│   └── full_audit.py     # audit  Excel ⇄ JSON ⇄ PostgreSQL
├── frontend/
│   └── index.html        # web app (fetches /api/products)
└── data/
    ├── raw/              # source Excel
    └── processed/        # generated JSON
```

## Data flow

```
Excel ──extract_data──▶ stock_data.json ──setup_database──▶ PostgreSQL ──API──▶ Frontend
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # then edit DB credentials
```

## Load data into the database (run once / when Excel changes)

```bash
python scripts/extract_data.py     # Excel → JSON
python scripts/setup_database.py   # JSON  → PostgreSQL
python scripts/verify_data.py      # optional: confirm Excel == DB
```

## Run the app

```bash
python server/app.py
```

Then open http://127.0.0.1:8000

## API

| Method | Endpoint         | Description                                  |
|--------|------------------|----------------------------------------------|
| GET    | `/`              | Web app (frontend)                           |
| GET    | `/api/products`  | All products + daily movements (from DB)     |
| GET    | `/api/health`    | DB connectivity check                        |
```
