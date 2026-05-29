---
title: Project Structure
created: 2026-05-29
tags: [architecture, project-structure]
---

# Project Structure

```
stock_movement/
├── .env                  # DB credentials (gitignored)
├── .env.example          # template
├── .gitignore
├── README.md
├── requirements.txt
├── config.py             # central config: loads .env → paths + DB
│
├── server/
│   └── app.py            # Flask API + serves frontend
│
├── scripts/              # ETL / tooling
│   ├── extract_data.py   # Excel → JSON
│   ├── setup_database.py # JSON  → PostgreSQL
│   ├── verify_data.py    # verify Excel ⇄ DB
│   └── full_audit.py     # audit Excel ⇄ JSON ⇄ DB
│
├── frontend/
│   └── index.html        # web app (fetch /api/products)
│
├── data/
│   ├── raw/              # source Excel (gitignored)
│   └── processed/        # generated JSON (gitignored)
│
└── docs/                 # ← this vault
```

## ไฟล์สำคัญ

### `config.py`
ศูนย์กลาง config ทั้งหมด — ทุก script + server import จากที่นี่
- โหลด `.env` ด้วย `python-dotenv`
- กำหนด `ROOT`, `DATA_DIR`, `RAW_DIR`, `PROCESSED_DIR`, `FRONTEND_DIR`
- กำหนด `EXCEL_PATH`, `JSON_PATH`, `COMPACT_JSON_PATH`
- กำหนด `DB` dict, `DB_SCHEMA`, `SERVER_HOST`, `SERVER_PORT`

### `.env` (gitignored)
```
DB_HOST=192.168.0.110
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres123
DB_SCHEMA=stock_online
EXCEL_FILE=Stock Online_JLC GROUP 2026.xlsx
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
```

### `server/app.py`
Flask backend — ดู [[API-Reference]]

### `scripts/*`
ETL pipeline — ดู [[Data-Flow]]

### `frontend/index.html`
HTML/JS single page — fetch จาก `/api/products` ตอนโหลด

## ทำไมโครงสร้างแบบนี้

| ปัญหาเดิม (flat) | แก้ด้วยโครงสร้างใหม่ |
|---|---|
| DB credential hardcode ในหลายไฟล์ | รวมไว้ที่ `.env` ผ่าน `config.py` |
| HTML embed JSON 1.7 MB ในตัว | frontend fetch จาก API → 17 KB |
| ไฟล์ raw/processed/source ปนกัน | แยก `data/raw`, `data/processed`, `scripts/` |
| ไม่มี server | เพิ่ม `server/app.py` (Flask) |
| ไม่มี doc | เพิ่ม `docs/` (Obsidian vault) |

## Related

- [[Data-Flow]]
- [[API-Reference]]
- [[Database-Schema]]
