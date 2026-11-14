#!/usr/bin/env python3
"""Bina semula tanaman.db daripada schema.sql dan seed.sql."""
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "tanaman.db"

if DB.exists():
    DB.unlink()

con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys = ON")
for name in ("schema.sql", "seed.sql"):
    con.executescript((HERE / name).read_text(encoding="utf-8"))
con.commit()

print(f"Siap: {DB}")
for (table,) in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
):
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:25} {n} baris")
con.close()
