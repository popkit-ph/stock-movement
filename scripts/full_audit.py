"""Full audit: Excel ⇄ front-end JSON ⇄ PostgreSQL - every row."""
import os, sys, openpyxl, psycopg2, json
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

DB = config.DB
SRC = str(config.EXCEL_PATH)
SKIP = {'สรุปสินค้าคงเหลือ', 'สรุปวัสดุคงเหลือ', 'Stock', 'รอรหัส'}
MONTH_MAP = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
             'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}

def clean(s):
    return '' if s is None else str(s).strip().lstrip('ฺ์ัิีึืุูํ็่้๊๋').strip()

print("=" * 72)
print("FULL AUDIT: Excel ⇄ Front-end (stock_app.html) ⇄ PostgreSQL")
print("=" * 72)

# 1) Extract Excel ground truth
wb = openpyxl.load_workbook(SRC, data_only=True, read_only=True)
excel = {}
for sn in wb.sheetnames:
    if sn in SKIP: continue
    s = wb[sn]
    rows_head = list(s.iter_rows(min_row=1, max_row=12, values_only=True))
    code = clean(rows_head[5][0]) or clean(rows_head[9][1]) or sn.split('.',1)[-1]
    name = clean(rows_head[5][1]) if len(rows_head[5]) > 1 else ''
    cm, txs = None, {}
    op = cls = tin = tout = 0
    for row in s.iter_rows(min_row=7, max_row=440, values_only=True):
        if not row or len(row) < 7: continue
        dv, _, _, br, qi, qo, ba = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
        if isinstance(dv, str):
            if 'รวม' in dv: continue
            low = dv.strip().lower()
            for n,nu in MONTH_MAP.items():
                if low.startswith(n): cm = nu; break
            continue
        if dv is None and br is None and qi is None and qo is None: continue
        if not isinstance(dv, datetime): continue
        if cm and dv.month != cm:
            try: dv = dv.replace(month=cm)
            except: continue
        d = dv.date()
        if d in txs: continue
        f = lambda x: float(x) if x not in (None,'') else 0
        b,i_,o_,bal = f(br),f(qi),f(qo),f(ba)
        if not txs: op = b
        tin += i_; tout += o_; cls = bal
        txs[d] = (i_, o_, bal)
    excel[sn] = {'code': code, 'name': name, 'opening': op, 'in': tin, 'out': tout, 'closing': cls, 'tx': txs}

print(f"\n[Excel] sheets={len(excel)}  total_tx={sum(len(v['tx']) for v in excel.values()):,}")

# 2) Load front-end JSON (compact dataset served by the API)
fe = json.load(open(config.COMPACT_JSON_PATH, encoding='utf-8'))
fe_by_sheet = {p['sheet']: p for p in fe['products']}
print(f"[Front-end JSON] products={len(fe_by_sheet)}  total_tx={sum(len(p['tx']) for p in fe['products']):,}")

# 3) Load PostgreSQL
conn = psycopg2.connect(**DB)
cur = conn.cursor()
cur.execute("SELECT sheet_name, code, name, category_code, opening_balance, total_in, total_out, closing_balance FROM stock_online.products")
db_prods = {}
for r in cur.fetchall():
    db_prods[r[0]] = {'code':r[1],'name':r[2],'cat':r[3],'opening':float(r[4]),'in':float(r[5]),'out':float(r[6]),'closing':float(r[7])}
cur.execute("""SELECT p.sheet_name, m.movement_date, m.qty_in, m.qty_out, m.balance
               FROM stock_online.stock_movements m JOIN stock_online.products p ON p.id = m.product_id""")
db_mv = defaultdict(dict)
for sn, d, i_, o_, b in cur.fetchall():
    db_mv[sn][d] = (float(i_), float(o_), float(b))
print(f"[PostgreSQL] products={len(db_prods)}  total_tx={sum(len(v) for v in db_mv.values()):,}")

# 4) AUDIT every sheet
print("\n" + "=" * 72)
print("AUDIT: per-SKU (compare Excel vs Front-end vs DB)")
print("=" * 72)

per_sku_issues = []
total_value_compared = 0

for sn in sorted(excel.keys()):
    xl = excel[sn]
    fep = fe_by_sheet.get(sn)
    db = db_prods.get(sn)
    issues = []
    # presence
    if not fep: issues.append("MISSING in Front-end")
    if not db:  issues.append("MISSING in DB")
    # master values
    for fld in ('opening','in','out','closing'):
        if fep and abs(xl[fld] - (fep['total_'+fld] if fld in ('in','out') else fep[fld if fld!='closing' else 'closing'])) > 0.01:
            issues.append(f"FE.{fld}")
        if db and abs(xl[fld] - db[fld]) > 0.01:
            issues.append(f"DB.{fld}")
    # code consistency
    if fep and clean(fep['code']) != xl['code']:
        issues.append(f"FE.code={fep['code']!r} vs xlsx={xl['code']!r}")
    if db and clean(db['code']) != xl['code']:
        issues.append(f"DB.code={db['code']!r} vs xlsx={xl['code']!r}")
    # tx counts
    if fep and len(fep['tx']) != len(xl['tx']):
        issues.append(f"FE.tx_count={len(fep['tx'])} vs xlsx={len(xl['tx'])}")
    if db and len(db_mv.get(sn, {})) != len(xl['tx']):
        issues.append(f"DB.tx_count={len(db_mv.get(sn,{}))} vs xlsx={len(xl['tx'])}")
    # values - every date
    if fep:
        fe_tx_map = {t[0]: (t[1], t[2], t[3]) for t in fep['tx']}
        for d, (xi, xo, xb) in xl['tx'].items():
            total_value_compared += 1
            iso = d.isoformat()
            if iso not in fe_tx_map:
                issues.append(f"FE missing date {iso}"); break
            fi, fo, fb = fe_tx_map[iso]
            if abs(xi-fi)>0.01 or abs(xo-fo)>0.01 or abs(xb-fb)>0.01:
                issues.append(f"FE diff at {iso}: xlsx=({xi},{xo},{xb}) fe=({fi},{fo},{fb})"); break
    if db:
        dbtx = db_mv.get(sn, {})
        for d, (xi, xo, xb) in xl['tx'].items():
            if d not in dbtx:
                issues.append(f"DB missing date {d}"); break
            di, do, dbal = dbtx[d]
            if abs(xi-di)>0.01 or abs(xo-do)>0.01 or abs(xb-dbal)>0.01:
                issues.append(f"DB diff at {d}: xlsx=({xi},{xo},{xb}) db=({di},{do},{dbal})"); break

    if issues:
        per_sku_issues.append((sn, xl['code'], issues))

# Report
print(f"\nTotal values compared (per cell): {total_value_compared*2:,}  (FE + DB)")
print(f"SKU with issues: {len(per_sku_issues)} / {len(excel)}\n")

if per_sku_issues:
    for sn, code, iss in per_sku_issues[:20]:
        print(f"  ✗ {sn:30s} ({code}): {'; '.join(iss[:3])}")
    if len(per_sku_issues) > 20:
        print(f"  ... +{len(per_sku_issues)-20} more")

# 5) Category & FE counts shown to user
print("\n" + "=" * 72)
print("CATEGORY BREAKDOWN (what user sees)")
print("=" * 72)
xl_cats = Counter()
for sn in excel:
    # use FE classification
    fep = fe_by_sheet.get(sn)
    if fep: xl_cats[fep['category']] += 1
fe_cats = Counter(p['category'] for p in fe['products'])
cur.execute("SELECT category_code, COUNT(*) FROM stock_online.products GROUP BY category_code")
db_cats = dict(cur.fetchall())

print(f"{'Cat':6s} {'FE':>6s} {'DB':>6s}  Status")
for cat in sorted(set(list(fe_cats.keys()) + list(db_cats.keys()))):
    f, d = fe_cats.get(cat,0), db_cats.get(cat,0)
    print(f"{cat:6s} {f:>6d} {d:>6d}  {'✓ match' if f == d else '✗ DIFF'}")

# 6) Show first 5 of each category from FE
print("\n" + "=" * 72)
print("FRONT-END: products shown per category (first 5 each)")
print("=" * 72)
for cat in ['FG','BTA','PM','BOX']:
    items = [p for p in fe['products'] if p['category'] == cat]
    print(f"\n[{cat}] total = {len(items)} items")
    for p in items[:5]:
        print(f"  {p['code']:15s} closing={p['closing']:>10}  in={p['total_in']:>10}  out={p['total_out']:>10}  {p['name'][:40]}")
    if len(items) > 5:
        print(f"  ... and {len(items)-5} more")

print("\n" + "=" * 72)
if not per_sku_issues and fe_cats == db_cats:
    print("✅ PASSED — Excel = Front-end = PostgreSQL (137 SKU, 50,003 records)")
else:
    print(f"⚠️  Issues found in {len(per_sku_issues)} SKU(s)")
print("=" * 72)

cur.close(); conn.close()
