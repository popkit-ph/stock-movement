---
title: Data Flow
created: 2026-05-29
tags: [architecture, data-flow, etl]
---

# Data Flow

```
Excel ──extract_data──▶ JSON ──setup_database──▶ PostgreSQL ──API──▶ Frontend
```

## ขั้นตอน

### 1. Excel → JSON (`scripts/extract_data.py`)

- อ่าน `data/raw/Stock Online_JLC GROUP 2026.xlsx` (path จาก `config.EXCEL_PATH`)
- ข้าม sheet: `สรุปสินค้าคงเหลือ`, `สรุปวัสดุคงเหลือ`, `Stock`, `รอรหัส`
- map sheet → category code:
  - `FG` (Finished Goods)
  - `BTA` (Bottle/Tube/Accessory)
  - `PM` (Packaging Material)
  - `BOX`
- เขียน 2 ไฟล์ออก:
  - `data/processed/stock_data.json` (เต็ม, ~10 MB)
  - `data/processed/stock_data_compact.json` (compact format, ~1.7 MB)

### 2. JSON → PostgreSQL (`scripts/setup_database.py`)

- เชื่อม DB ผ่าน `config.DB`
- สร้าง schema `stock_online` (ถ้ายังไม่มี)
- สร้างตาราง `products`, `stock_movements` — ดู [[Database-Schema]]
- TRUNCATE + INSERT ใหม่ทั้งหมด
- รายงาน: 137 products, 50,003 movement rows

### 3. PostgreSQL → API (`server/app.py`)

- Flask app เปิด port 8000
- endpoint `/api/products` query DB → return JSON
- รูปแบบที่ส่งให้ frontend = compact format เดียวกับ JSON file

### 4. API → Frontend (`frontend/index.html`)

- โหลดหน้า → fetch `/api/products`
- เก็บไว้ใน global `DB = { products: [...] }`
- filter/sort/render ด้วย JS ทั้งหมด client-side

## Compact format

ทุกขั้นใช้รูปแบบเดียวกัน — ทำให้ frontend ไม่ต้องเปลี่ยน logic

```js
{
  generated_at: "2026-05-29T...",
  product_count: 137,
  products: [
    {
      sheet:    "FG-001",         // sheet name in Excel
      code:     "FG-001",         // product code
      name:     "ครีมแตงโม",
      category: "FG",
      opening:  1000,             // opening balance (ยอดยกมา)
      total_in: 50000,            // ผลรวมรับเข้าทั้งปี
      total_out: 48500,           // ผลรวมจ่ายออกทั้งปี
      closing:  2500,             // ยอดคงเหลือสิ้นปี
      tx: [
        // [date, qty_in, qty_out, balance, doc_no, note]
        ["2026-01-05", 1000, 0, 2000, "DOC-001", ""],
        ["2026-01-06", 0, 500, 1500, "INV-A1", "ส่งลูกค้า X"],
        ...
      ]
    },
    ...
  ]
}
```

## Tools

- [[../work-log/2026-05-29-fullstack-restructure]] — ตอน restructure
- `scripts/verify_data.py` — ตรวจว่า DB ตรงกับ Excel
- `scripts/full_audit.py` — audit 3 ทาง: Excel ⇄ JSON ⇄ DB

## Related

- [[Project-Structure]]
- [[API-Reference]]
- [[Database-Schema]]
