#!/usr/bin/env python3
"""BlackRoad Lending System — DeFi-style lending pool with interest calculation."""
import sqlite3, os, time, json

DB = os.path.expanduser("~/.blackroad/lending.db")

def init():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript("""
        CREATE TABLE IF NOT EXISTS pools (
            id TEXT PRIMARY KEY, asset TEXT, total_supplied REAL,
            total_borrowed REAL, base_rate REAL, updated_at REAL
        );
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pool_id TEXT,
            user TEXT, type TEXT, amount REAL, interest_rate REAL,
            opened_at REAL, accrued_interest REAL DEFAULT 0
        );
    """)
    c.commit()
    return c

def create_pool(id: str, asset: str, base_rate: float = 0.05):
    c = init()
    c.execute("INSERT OR IGNORE INTO pools VALUES (?,?,0,0,?,?)", (id,asset,base_rate,time.time()))
    c.commit(); print(f"✓ Pool {id} ({asset}) created, base rate: {base_rate*100:.1f}%")

def utilization_rate(total_borrowed: float, total_supplied: float) -> float:
    return total_borrowed / total_supplied if total_supplied > 0 else 0

def borrow_rate(pool_id: str) -> float:
    c = init()
    row = c.execute("SELECT total_supplied,total_borrowed,base_rate FROM pools WHERE id=?", (pool_id,)).fetchone()
    if not row: return 0.0
    u = utilization_rate(row[1], row[0])
    return row[2] + u * 0.2  # linear model: base + 20% * utilization

def pool_stats():
    c = init()
    rows = c.execute("SELECT id,asset,total_supplied,total_borrowed,base_rate FROM pools").fetchall()
    print("\n💰 BlackRoad Lending Pools\n")
    for r in rows:
        u = utilization_rate(r[3],r[2])
        br = borrow_rate(r[0])
        print(f"  {r[0]:<15} {r[1]:<6} supplied=${r[2]:>10,.2f}  borrowed=${r[3]:>10,.2f}  util={u*100:.1f}%  borrow_rate={br*100:.2f}%")

if __name__ == "__main__":
    create_pool("ETH-POOL", "ETH", 0.03)
    create_pool("BTC-POOL", "BTC", 0.02)
    pool_stats()

