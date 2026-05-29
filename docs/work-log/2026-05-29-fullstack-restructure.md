---
date: 2026-05-29
title: Restructure flat → full-stack + .env + Flask API
status: done
tags: [work-log, refactor, backend, etl, infrastructure]
---

# Restructure flat → full-stack + .env + Flask API

## เป้าหมาย

จัดระเบียบโครงสร้างแอปจาก flat (ทุกไฟล์อยู่ root) ให้เป็น **full-stack project structure**:
- แยก server / scripts / frontend / data
- ใช้ `.env` เก็บ DB credentials
- ทำให้ frontend อ่านจาก PostgreSQL ผ่าน API (เลิก embed JSON ในตัว HTML)

## สิ่งที่เปลี่ยน

### สร้างใหม่
- `config.py` — central config, load `.env`, define paths + DB
- `.env` + `.env.example` — DB credentials, schema, server host/port
- `.gitignore` — ignore `.env`, `__pycache__`, `data/raw/*.xlsx`, `data/processed/*.json`
- `requirements.txt` — Flask, psycopg2-binary, openpyxl, python-dotenv
- `README.md` — overview + setup + API
- `server/app.py` — Flask app: `/`, `/api/health`, `/api/products`

### ย้ายไฟล์
- `Stock Online_JLC GROUP 2026.xlsx` → `data/raw/`
- `stock_data.json`, `stock_data_compact.json` → `data/processed/`
- `extract_data.py`, `setup_database.py`, `verify_data.py`, `full_audit.py` → `scripts/`
- `stock_app.html` → `frontend/index.html`

### แก้ scripts
- ทุก script ใน `scripts/` เพิ่ม `sys.path.insert + import config`
- เลิก hardcode DB credentials → ใช้ `config.DB`
- ใช้ `config.EXCEL_PATH`, `config.JSON_PATH`, `config.COMPACT_JSON_PATH`
- `full_audit.py` อ่าน JSON compact แทน parse HTML

### แก้ frontend
- ลบ embedded JSON 1.7 MB (บรรทัด 174) ด้วย `sed -i '174d'`
- เปลี่ยน `const DB = JSON.parse(...)` → `let DB = { products: [] };`
- เพิ่ม `async loadData()` ที่ fetch `/api/products`
- ขนาด HTML: 1.7 MB → 17 KB

## เหตุผล / การตัดสินใจ

| เรื่อง | ทางเลือก | ที่เลือก | เพราะ |
|---|---|---|---|
| Backend framework | Flask / FastAPI | **Flask** | ใช้ template เดิม, requirement น้อย, deploy ง่าย |
| Serve static | nginx / Flask | **Flask** | dev simple, ขนาดเล็ก, ไม่ต้อง 2 process |
| Cross-origin | CORS / same origin | **same origin** | Flask serve frontend ด้วย → ไม่ต้อง CORS |
| Data pipeline | Direct Excel→DB / Excel→JSON→DB | **คง JSON ตรงกลาง** | user ขอเก็บ JSON ไว้ตามเดิม |

## ปัญหาที่เจอ

- **Background task fail (exit 144)** — ใช้ `setsid python3 server/app.py > /tmp/stock_server.log 2>&1 < /dev/null & disown` แล้วผ่าน
- **Edit ไฟล์หลัง move** — ต้อง Read ก่อน Edit (เครื่องมือ require)
- **embedded JSON 1.7 MB เป็น 1 บรรทัด** — ใช้ `sed -i '174d'` ตัดออก

## ทดสอบ

```bash
curl http://127.0.0.1:8000/api/health
# {"database":"connected","status":"ok"}

curl http://127.0.0.1:8000/api/products | jq '.product_count, (.products | map(.tx | length) | add)'
# 137
# 50003
```

## Related

- [[../architecture/Project-Structure]]
- [[../architecture/Data-Flow]]
- [[../architecture/API-Reference]]
- [[2026-05-29-frontend-ux-improvements]]
