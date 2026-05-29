---
date: 2026-05-29
title: Admin mode — เพิ่มสินค้า + บันทึกรับจ่ายรายวัน + autocomplete
status: done
tags: [work-log, feature, backend, frontend, admin]
---

# Admin mode — เพิ่มสินค้า + บันทึกรับจ่ายรายวัน

## เป้าหมาย

เพิ่มความสามารถ **เขียนข้อมูล** ให้แอป (เดิม read-only):
1. เพิ่มรายการสินค้าใหม่ได้
2. บันทึก/อัปเดต รับ-จ่าย รายวัน → คำนวณคงเหลือใหม่อัตโนมัติ
3. ช่องบันทึกรายวันใช้ **search + autocomplete** แนะนำสินค้าที่ชื่อคล้ายกัน

## การตัดสินใจ (จาก user)

- **Auth**: PIN ใน `.env` (`ADMIN_PIN`)
- **บันทึกรายวัน**: วันเดียวกัน → บวกเพิ่ม (accumulate), คนละวัน → สร้างแถวใหม่
- **Data source**: DB เป็นหลัก (Excel/JSON ไม่ sync กลับ)

## สิ่งที่เปลี่ยน

### `config.py` + `.env` + `.env.example`
- เพิ่ม `ADMIN_PIN` (อ่านจาก env, ค่าว่าง = ปิด admin)

### `server/app.py` — เพิ่ม write API
- `ADMIN_TOKENS` (set ใน memory), decorator `require_admin` ตรวจ `Authorization: Bearer <token>`
- `POST /api/admin/login` — แลก PIN เป็น token
- `POST /api/admin/logout` — เพิกถอน token
- `POST /api/products` 🔒 — สร้างสินค้า (กันรหัส/sheet ซ้ำ → 409)
- `POST /api/movements` 🔒 — บันทึกรับ/จ่าย
  - UPSERT: `ON CONFLICT (product_id, movement_date)` → บวก qty เดิม
  - เรียก `recompute_product()` แล้วคืน product (compact shape)
- helper `recompute_product()` — คำนวณ running balance + brought_forward ทุกแถว + อัปเดต aggregate (`total_in/out/closing`)
- helper `fetch_product()` — ดึง product เดียวในรูปแบบ compact
- `/api/health` เพิ่มฟิลด์ `admin_enabled`

### `frontend/index.html` — Admin UI
- ปุ่ม 🔑 Admin มุมขวาบน → modal ใส่ PIN → เก็บ token ใน `sessionStorage`
- Admin toolbar (แถบเหลือง): เพิ่มสินค้าใหม่ / บันทึกรับ-จ่ายรายวัน / ออกจาก Admin
- **Modal เพิ่มสินค้า**: รหัส, หมวด, ชื่อ, ยอดยกมา
- **Modal บันทึกรายวัน**:
  - `searchProducts()` + `renderAc()` — autocomplete (startswith ก่อน, ไฮไลต์ `<mark>`, สูงสุด 10, โชว์คงเหลือ)
  - keyboard nav (↑/↓/Enter) ใน dropdown
  - การ์ดสินค้าที่เลือก + preview "คงเหลือใหม่ = คงเหลือ + รับ − จ่าย" สดๆ
  - submit แล้ว reset qty ให้บันทึกตัวต่อไปได้ทันที (เก็บสินค้าที่เลือกไว้)
- `adminFetch()` wrapper แนบ token + จัดการ 401 (เด้งออก admin)
- `mergeProduct()` — อัปเดต product ใน `DB.products` แล้ว re-render
- toast แจ้งผล (`#toasts`)

### `.claude/launch.json`
- config สำหรับ Claude Preview รัน `python3 server/app.py` (dev)

## ทดสอบ

### API (`/tmp/test_admin.py` — 11 เคส ผ่านหมด)
- login ผิด/ถูก, write ไม่มี token → 401
- create product → 201, ซ้ำ → 409
- movement วันเดียวกัน → บวกเพิ่ม (50 in, ต่อมา 20 out → คงเหลือ 130)
- movement คนละวัน → แถวใหม่
- **backdated insert** → balance แถวหลังเลื่อนถูกต้อง (closing 110)
- qty 0 ทั้งคู่ → 400, product ไม่มี → 404

### Frontend (Claude Preview browser)
- login PIN 2026 → admin bar โผล่ ✓
- autocomplete "ครีม" → ไฮไลต์ + คงเหลือ ✓
- preview คงเหลือใหม่ ✓
- สร้าง UITEST-1 (opening 500) → toast + KPI 137→138 + คงเหลือ +500 ✓
- จ่าย 120 → "คงเหลือใหม่ 380" + reset ฟอร์ม ✓
- ไม่มี console error ✓
- (ลบ test data ออกหลังทดสอบ — กลับมา 137)

## ขั้นถัดไป (ถ้าต้องการต่อ)

- แก้ไข/ลบ movement (ตอนนี้เพิ่ม/บวกเท่านั้น)
- ปุ่ม export DB → Excel
- audit log ว่าใครแก้อะไรเมื่อไหร่

## Related

- [[../architecture/API-Reference]]
- [[../architecture/Database-Schema]]
- [[2026-05-29-fullstack-restructure]]
