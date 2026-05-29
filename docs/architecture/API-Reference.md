---
title: API Reference
created: 2026-05-29
tags: [architecture, api, backend]
---

# API Reference

Flask backend ใน `server/app.py`. รัน:

```bash
python server/app.py
```

default: `http://127.0.0.1:8000`

## Endpoints

### `GET /`
ส่ง `frontend/index.html`

### `GET /api/health`
ตรวจการเชื่อม DB

**Response 200**
```json
{ "status": "ok", "database": "connected" }
```

**Response 503**
```json
{ "status": "error", "database": "unreachable", "detail": "<err>" }
```

### `GET /api/products`
รายการสินค้าทั้งหมด + movement รายวัน

**Response 200**
```json
{
  "generated_at": "2026-05-29T10:00:00",
  "product_count": 137,
  "products": [
    {
      "sheet": "FG-001",
      "code": "FG-001",
      "name": "...",
      "category": "FG",
      "opening": 1000,
      "total_in": 50000,
      "total_out": 48500,
      "closing": 2500,
      "tx": [
        ["2026-01-05", 1000, 0, 2000, "DOC-001", ""]
      ]
    }
  ]
}
```

`tx` row = `[date, qty_in, qty_out, balance, doc_no, note]`

## SQL ที่ใช้

```sql
-- products
SELECT id, sheet_name, code, name, category_code,
       opening_balance, total_in, total_out, closing_balance
FROM stock_online.products
ORDER BY id;

-- stock_movements
SELECT product_id, movement_date, qty_in, qty_out, balance, doc_no, note
FROM stock_online.stock_movements
ORDER BY product_id, movement_date;
```

ดู schema ที่ [[Database-Schema]]

## Helper

`num(x)` — ทำให้ Decimal/None ออกเป็น int (ถ้าเป็นจำนวนเต็ม) หรือ float

## Notes

- ไม่มี CORS เพราะ frontend serve จาก Flask เดียวกัน (same origin)
- ไม่มี pagination — ส่งทั้งหมดในรอบเดียว (~50k tx rows OK สำหรับขนาดนี้)
- ทุก endpoint เปิด `psycopg2.connect()` + `conn.close()` per request — ไม่มี connection pool

## Related

- [[Project-Structure]]
- [[Database-Schema]]
- [[Data-Flow]]
