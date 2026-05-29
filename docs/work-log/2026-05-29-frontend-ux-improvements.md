---
date: 2026-05-29
title: Frontend UX — sticky bar/header, dynamic KPI, date range, header sort
status: done
tags: [work-log, feature, ui, frontend]
---

# Frontend UX — sticky bar/header, dynamic KPI, date range, header sort

## เป้าหมาย

ปรับ UX ของ `frontend/index.html` ตามที่ user request หลายรอบ:
1. ปักหมุด top bar (ไม่ย่อ/ขยายตาม scroll)
2. KPI ด้านบน dynamic ตาม filter
3. Modal summary dynamic ตามเดือนที่เลือก
4. เพิ่ม date range filter ในหน้าหลัก
5. เพิ่ม filter "จ่าย" ทั้ง 2 ทาง (มาก→น้อย / น้อย→มาก) เหมือนคงเหลือ
6. คลิกหัวคอลัมน์ "จ่าย" → toggle sort (desc → asc → default)
7. ปักหมุดหัวคอลัมน์ (sticky thead)

## สิ่งที่เปลี่ยน

ทุกการเปลี่ยนแปลงอยู่ใน `frontend/index.html`

### 1. Top bar pinned
- ลบ scroll listener ที่ toggle `.scrolled` class
- เก็บไว้แต่ resize listener สำหรับคำนวณ `--sticky-h`

### 2. Dynamic KPI
- `renderKPIs()` ใช้ `filtered` แทน `DB.products`
- เพิ่ม subtitle `<all_count>` ถ้า filtered ≠ total
- เรียก `renderKPIs()` ใน `applyFilters()` ทุกครั้ง

### 3. Dynamic modal summary per month
- แยก `renderSummary()` ออกมา
- 'all month' → ใช้ totals ของทั้งปี
- specific month → คำนวณจาก `p.tx` ที่ slice ใน month นั้น
  - `opening = balance สุดท้ายก่อนเดือนนี้` หรือ `p.opening` ถ้าไม่มี
  - `closing = balance สุดท้ายในเดือนนี้`
- เปลี่ยน label ตามเดือน เช่น "รับเข้า [ม.ค.]"

### 4. Date range filter
- เพิ่ม `<input type="date">` × 2 + ปุ่ม clear
- เพิ่ม `dateRange = { from, to }` global
- เพิ่ม `computeRangeStats(p)` คำนวณ in/out/opening/closing ในช่วง
- เพิ่ม `pStats(p)` — return range stats ถ้า rangeActive, ไม่งั้น return totals
- `renderKPIs`, `renderTable`, sort logic ทั้งหมดใช้ `pStats(p)`
- กรอง product ที่ไม่มี movement ในช่วงออก

### 5. Sort "จ่าย" 2 ทาง
- เพิ่ม option `out_asc` ใน dropdown
- เพิ่ม option `in_asc` ด้วย (สำหรับ "รับเข้า")
- เพิ่ม `negative_first` (anomaly: คงเหลือติดลบขึ้นก่อน)

### 6. Header sort toggle
- `<th id="th-out" class="num th-sort" onclick="toggleOutSort()">จ่าย <span class="th-arrow"></span></th>`
- `toggleOutSort()` cycle: `out_desc` → `out_asc` → `default`
- ใน `applyFilters()` sync visual: set `.active` class + arrow `▼`/`▲`
- CSS: `.th-sort` cursor pointer, `.th-sort.active` highlight สีน้ำเงิน

### 7. Sticky `<thead>`
- เปลี่ยน `#ptable` จาก `border-collapse: collapse` → `separate; border-spacing: 0`
- `#ptable thead th { position: sticky; top: var(--sticky-h); z-index: 30; background: #f9fafb; box-shadow: inset 0 -1px 0 #e5e7eb, 0 2px 4px rgba(0,0,0,.04); border-bottom: 0; }`

## เหตุผล / การตัดสินใจ

### ทำไม `border-collapse: separate`
`position: sticky` บน `<th>` ไม่ทำงานน่าเชื่อถือกับ `border-collapse: collapse` — เป็น browser-known issue. ต้องเปลี่ยนเป็น `separate` แล้วใช้ `box-shadow` แทน border-bottom

### ทำไม `pStats(p)`
หลีกเลี่ยงการคำนวณซ้ำในแต่ละ render — pre-compute `p._range` ตอน applyFilters ครั้งเดียว แล้ว KPI/table/sort ดึงผ่าน `pStats(p)` ที่อ่าน cached

### ทำไม dynamic KPI ใช้ `filtered`
user เลือก filter → เห็น "เฉพาะส่วนที่ filter" → ตัดสินใจได้ตรงกว่า KPI ทั้งหมด

## ปัญหาที่เจอ

- **Edit `<th class="num">จ่าย</th>` มี 2 ที่** (main table + modal table) → fix โดยใส่ context รอบๆ ใน old_string
- **User งงว่า BOX ติดลบขึ้นบนสุด** — อธิบายว่าเขาเลือก sort "จ่ายมาก→น้อย" และ BOX-0 จ่าย 293,131 จริง = สูงสุด → ถูกแล้ว. เพิ่ม option "⚠️ คงเหลือติดลบก่อน" สำหรับ anomaly detection

## ทดสอบ

- ลอง scroll → top bar + thead pinned, ไม่ย่อ
- เลือก category FG → KPI เปลี่ยนตาม
- เลือก range 2026-01-01 → 2026-03-31 → ตาราง + KPI แสดงเฉพาะของ Q1
- คลิก "จ่าย" → desc / คลิกอีก → asc / คลิกอีก → default
- คลิกเข้า modal → เปลี่ยนเดือน → summary เปลี่ยนตาม

## Related

- [[../architecture/Project-Structure]]
- [[../architecture/API-Reference]]
- [[2026-05-29-fullstack-restructure]]
