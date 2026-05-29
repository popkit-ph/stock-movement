---
title: Database Schema
created: 2026-05-29
tags: [architecture, database, postgresql]
---

# Database Schema

PostgreSQL schema: `stock_online`

## Tables

### `stock_online.products`

| column            | type          | note                          |
|-------------------|---------------|-------------------------------|
| `id`              | SERIAL PK     |                               |
| `sheet_name`      | TEXT          | ชื่อ sheet ใน Excel           |
| `code`            | TEXT          | รหัสสินค้า                    |
| `name`            | TEXT          | ชื่อสินค้า                    |
| `category_code`   | TEXT          | `FG` / `BTA` / `PM` / `BOX`   |
| `opening_balance` | NUMERIC       | ยอดยกมาต้นปี                  |
| `total_in`        | NUMERIC       | รวมรับเข้าทั้งปี              |
| `total_out`       | NUMERIC       | รวมจ่ายออกทั้งปี              |
| `closing_balance` | NUMERIC       | ยอดคงเหลือสิ้นปี              |

### `stock_online.stock_movements`

| column          | type      | note                              |
|-----------------|-----------|-----------------------------------|
| `id`            | SERIAL PK |                                   |
| `product_id`    | INT FK    | → `products.id`                   |
| `movement_date` | DATE      | วันที่เคลื่อนไหว                 |
| `qty_in`        | NUMERIC   | รับเข้า                           |
| `qty_out`       | NUMERIC   | จ่ายออก                           |
| `balance`       | NUMERIC   | balance หลังบันทึก                |
| `doc_no`        | TEXT      | เลขเอกสาร                         |
| `note`          | TEXT      | หมายเหตุ                          |

## ขนาดข้อมูล (ณ 2026-05-29)

- 137 products
- 50,003 movement rows

## Category codes

| code  | sheet name pattern  | ความหมาย              |
|-------|---------------------|------------------------|
| `FG`  | `FG-*`              | Finished Goods         |
| `BTA` | `BTA-*`             | Bottle/Tube/Accessory  |
| `PM`  | `PM-*`              | Packaging Material     |
| `BOX` | `BOX-*`             | กล่อง                  |

Sheet ที่ถูกข้าม (ไม่นำเข้า): `สรุปสินค้าคงเหลือ`, `สรุปวัสดุคงเหลือ`, `Stock`, `รอรหัส`

## DDL อยู่ที่ไหน

`scripts/setup_database.py` — สร้าง schema + table ถ้ายังไม่มี แล้ว TRUNCATE + INSERT จาก JSON

## Running balance + aggregate (สำคัญ)

- `stock_movements.balance` = **ยอดสะสม** (running) = opening + Σ(in − out) ถึงวันนั้น
- `stock_movements.brought_forward` = ยอดก่อนแถวนั้น
- `products.total_in/total_out/closing_balance` = aggregate (denormalized)

➡️ ทุกครั้งที่ **เพิ่ม/แก้ movement** ต้องเรียก `recompute_product()` ใน `server/app.py`
เพื่อคำนวณ balance ของแถวนั้น **และทุกแถวหลังจากนั้น** ใหม่ (เพราะยอดสะสมเลื่อน)
รวมถึงกรณีบันทึกย้อนหลัง (backdated)

Admin `POST /api/movements` ใช้ `ON CONFLICT (product_id, movement_date)` →
วันเดียวกันบวก qty เดิม, คนละวันสร้างแถวใหม่

## ตรวจสอบ

```bash
python scripts/verify_data.py   # ตรวจ Excel ⇄ DB
python scripts/full_audit.py    # ตรวจ Excel ⇄ JSON ⇄ DB
```

## Related

- [[Data-Flow]]
- [[API-Reference]]
- [[Project-Structure]]
