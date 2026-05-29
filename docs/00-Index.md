---
title: Index — Map of Content
created: 2026-05-29
tags: [moc, index]
---

# 00 — Index (MOC)

หน้าเริ่มต้นของ vault. ใช้เป็น hub ไปยังหน้าอื่นๆ

## Architecture

- [[architecture/Project-Structure]] — โครงสร้างโฟลเดอร์ + ไฟล์สำคัญ
- [[architecture/Data-Flow]] — Excel → JSON → PostgreSQL → API → Frontend
- [[architecture/API-Reference]] — endpoints ของ Flask
- [[architecture/Database-Schema]] — schema `stock_online` + ตาราง

## Work Log

ประวัติการแก้ไข เรียงจากใหม่ → เก่า

- [[work-log/2026-05-29-frontend-ux-improvements]] — sticky header, dynamic KPI, date range filter, header sort
- [[work-log/2026-05-29-fullstack-restructure]] — restructure flat → full-stack, .env, Flask API
- [[work-log/_template]] — template สำหรับ entry ใหม่

## Changelog

- [[CHANGELOG]] — สรุปการเปลี่ยนแปลงทั้งหมด (รวบยอด)

## Quick Reference

| สิ่งที่ต้องการ | ดูที่ |
|---|---|
| รันแอป | `python server/app.py` แล้วเปิด `http://127.0.0.1:8000` |
| รีโหลดข้อมูลจาก Excel | run `scripts/extract_data.py` → `scripts/setup_database.py` |
| เปลี่ยน DB credentials | แก้ไฟล์ `.env` (ดู `.env.example`) |
| ตรวจ DB ตรงกับ Excel | run `scripts/verify_data.py` หรือ `scripts/full_audit.py` |

## Tags ที่ใช้ในบ vault

- `#architecture` — เอกสารโครงสร้าง
- `#work-log` — บันทึกการทำงานแต่ละครั้ง
- `#frontend` `#backend` `#database` `#etl` — หมวดงาน
- `#bugfix` `#feature` `#refactor` `#ui` — ประเภทการเปลี่ยนแปลง
