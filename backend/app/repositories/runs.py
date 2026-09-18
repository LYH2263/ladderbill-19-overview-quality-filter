import json
import sqlite3
from datetime import datetime, timezone


def insert(
    conn: sqlite3.Connection,
    kind: str,
    payload: dict,
    result: dict,
    account_id: int | None = None,
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        """
        INSERT INTO calc_runs(kind, account_id, input_json, result_json, created_at)
        VALUES (?,?,?,?,?)
        """,
        (kind, account_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_recent(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    q = """
    SELECT id, kind, account_id, input_json, result_json, created_at
    FROM calc_runs ORDER BY id DESC LIMIT ?
    """
    return [dict(r) for r in conn.execute(q, (limit,)).fetchall()]


def latest_by_account(conn: sqlite3.Connection) -> dict[int, dict]:
    """每户最近一条 calc_run，按 account_id 索引。"""
    q = """
    SELECT r.id, r.kind, r.account_id, r.result_json, r.created_at
    FROM calc_runs r
    JOIN (
        SELECT account_id, MAX(id) AS max_id
        FROM calc_runs
        WHERE account_id IS NOT NULL
        GROUP BY account_id
    ) latest ON latest.max_id = r.id
    """
    return {row["account_id"]: dict(row) for row in conn.execute(q).fetchall()}


def get(conn: sqlite3.Connection, run_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return dict(row) if row else None
