"""Flask backend: serves the frontend and a JSON API backed by PostgreSQL."""
import os
import sys
from datetime import datetime
from collections import defaultdict

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

app = Flask(__name__, static_folder=None)


def get_conn():
    return psycopg2.connect(**config.DB)


def num(x):
    """Decimal/None -> JSON-friendly int or float."""
    if x is None:
        return 0
    f = float(x)
    return int(f) if f.is_integer() else f


@app.route("/")
def index():
    return send_from_directory(config.FRONTEND_DIR, "index.html")


@app.route("/api/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return jsonify(status="ok", database="connected")
    except Exception as e:
        return jsonify(status="error", database="unreachable", detail=str(e)), 503


@app.route("/api/products")
def products():
    """Full dataset in the compact shape the frontend expects."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(f"""
        SELECT id, sheet_name, code, name, category_code,
               opening_balance, total_in, total_out, closing_balance
        FROM {config.DB_SCHEMA}.products
        ORDER BY id
    """)
    prod_rows = cur.fetchall()

    cur.execute(f"""
        SELECT product_id, movement_date, qty_in, qty_out, balance, doc_no, note
        FROM {config.DB_SCHEMA}.stock_movements
        ORDER BY product_id, movement_date
    """)
    tx_by_product = defaultdict(list)
    for r in cur.fetchall():
        tx_by_product[r[0]].append([
            r[1].isoformat() if r[1] else "",
            num(r[2]), num(r[3]), num(r[4]),
            r[5] or "", r[6] or "",
        ])

    cur.close()
    conn.close()

    products_out = [{
        "sheet": p["sheet_name"],
        "code": p["code"],
        "name": p["name"] or "",
        "category": p["category_code"],
        "opening": num(p["opening_balance"]),
        "total_in": num(p["total_in"]),
        "total_out": num(p["total_out"]),
        "closing": num(p["closing_balance"]),
        "tx": tx_by_product.get(p["id"], []),
    } for p in prod_rows]

    return jsonify(
        generated_at=datetime.now().isoformat(),
        product_count=len(products_out),
        products=products_out,
    )


if __name__ == "__main__":
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=True)
