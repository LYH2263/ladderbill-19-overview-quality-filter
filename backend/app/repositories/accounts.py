import sqlite3

# 名称中带该标记的户号视为偏高种子户（dirty），其余为 clean。
DIRTY_KEYWORD = "种子"


def _quality_clause(quality: str | None) -> tuple[str, tuple]:
    if quality == "dirty":
        return " WHERE name LIKE ?", (f"%{DIRTY_KEYWORD}%",)
    if quality == "clean":
        return " WHERE name NOT LIKE ?", (f"%{DIRTY_KEYWORD}%",)
    return "", ()


def list_all(conn: sqlite3.Connection, quality: str | None = None) -> list[dict]:
    where, params = _quality_clause(quality)
    q = f"SELECT * FROM accounts{where} ORDER BY id"
    return [dict(r) for r in conn.execute(q, params).fetchall()]


def count_all(conn: sqlite3.Connection, quality: str | None = None) -> int:
    where, params = _quality_clause(quality)
    q = f"SELECT COUNT(*) c FROM accounts{where}"
    return int(conn.execute(q, params).fetchone()["c"])


def get(conn: sqlite3.Connection, account_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
    return dict(row) if row else None
