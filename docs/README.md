---
title: Stock Movement Vault
created: 2026-05-29
tags: [vault-home, jlc-group, stock-movement]
---

# Stock Movement — Docs Vault

โฟลเดอร์นี้คือ **Obsidian vault** เก็บประวัติการพัฒนา, สถาปัตยกรรม, และ changelog ของแอป **Stock Movement (JLC GROUP 2026)**

## วิธีใช้กับ Obsidian

1. เปิด Obsidian → `Open folder as vault` → เลือกโฟลเดอร์ `docs/` นี้
2. เริ่มที่ [[00-Index]] (MOC — Map of Content)
3. เปิด setting → Files & Links → **เปิด wikilinks** เพื่อให้ `[[...]]` ทำงาน

## โครงสร้าง

```
docs/
├── README.md                    ← คุณอยู่ที่นี่
├── 00-Index.md                  ← MOC หลัก (เริ่มอ่านจากที่นี่)
├── CHANGELOG.md                 ← สรุปการเปลี่ยนแปลงทั้งหมด
├── architecture/
│   ├── Project-Structure.md
│   ├── Data-Flow.md
│   ├── API-Reference.md
│   └── Database-Schema.md
└── work-log/
    ├── _template.md
    ├── 2026-05-29-fullstack-restructure.md
    └── 2026-05-29-frontend-ux-improvements.md
```

## เพิ่ม work-log ใหม่ยังไง

1. copy `work-log/_template.md` → ตั้งชื่อตามรูปแบบ `YYYY-MM-DD-<topic>.md`
2. เติม frontmatter (`date`, `tags`, `status`)
3. ใส่ลิงก์ใน [[00-Index]] section "Work Log"
4. update [[CHANGELOG]] ถ้าเป็น change ที่สำคัญ
