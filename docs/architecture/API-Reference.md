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
{ "status": "ok", "database": "connected", "admin_enabled": true }
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

## Admin (write) endpoints 🔒

ต้องมี header `Authorization: Bearer <token>` ยกเว้น login. token ได้จาก `/api/admin/login` (เก็บใน memory ของ server — หายเมื่อ restart)

### `POST /api/admin/login`
แลก PIN เป็น token

**Body** `{ "pin": "2026" }`
**200** `{ "status": "ok", "token": "<hex>" }` · **401** PIN ผิด · **403** ยังไม่ตั้ง `ADMIN_PIN`

### `POST /api/admin/logout` 🔒
เพิกถอน token ปัจจุบัน → `{ "status": "ok" }`

### `POST /api/products` 🔒
สร้างสินค้าใหม่

**Body**
```json
{ "code": "FG-100", "name": "...", "category": "FG", "opening_balance": 0 }
```
- `category` ต้องเป็น FG / BTA / PM / BOX
- `sheet_name` ไม่ส่งก็ได้ (default = code)
- **201** `{ "status": "ok", "product": {...} }`
- **400** ข้อมูลไม่ครบ · **409** รหัส/sheet ซ้ำ

### `POST /api/movements` 🔒
บันทึก/อัปเดต รับ-จ่าย รายวัน

**Body**
```json
{ "code": "FG-100", "date": "2026-05-29",
  "qty_in": 50, "qty_out": 0, "doc_no": "PO-1", "note": "" }
```
- วันเดียวกัน → **บวกเพิ่ม** ของเดิม (UPSERT) · คนละวัน → แถวใหม่
- หลังบันทึกจะ **คำนวณ balance + aggregate ใหม่ทั้งสาย** (`recompute_product`)
- **200** `{ "status": "ok", "product": {...} }` (product ที่อัปเดตแล้ว)
- **400** qty ติดลบ / 0 ทั้งคู่ / วันที่ผิดรูปแบบ · **404** ไม่พบรหัส

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

- `num(x)` — ทำให้ Decimal/None ออกเป็น int (ถ้าเป็นจำนวนเต็ม) หรือ float
- `fetch_product(cur, id)` — ดึง product เดียวในรูปแบบ compact (มี tx)
- `recompute_product(cur, id)` — คำนวณ running balance ทุกแถว + aggregate ใหม่ (เรียกหลังเขียน movement)
- `require_admin` (decorator) — ตรวจ `Authorization: Bearer <token>` กับ `ADMIN_TOKENS`

## Notes

- ไม่มี CORS เพราะ frontend serve จาก Flask เดียวกัน (same origin)
- ไม่มี pagination — ส่งทั้งหมดในรอบเดียว (~50k tx rows OK สำหรับขนาดนี้)
- ทุก endpoint เปิด `psycopg2.connect()` + `conn.close()` per request — ไม่มี connection pool
- admin token เก็บใน memory → restart server แล้วต้อง login ใหม่
- `ADMIN_PIN` ตั้งใน `.env` (ค่าว่าง = ปิด admin ทั้งหมด)

## Related

- [[Project-Structure]]
- [[Database-Schema]]
- [[Data-Flow]]
