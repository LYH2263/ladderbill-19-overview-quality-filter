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


def latest_by_account(
    conn: sqlite3.Connection, account_ids: list[int] | None = None
) -> dict[int, dict]:
    """每个户号最近一次关联运行，按 account_id 索引。"""
    scope = ""
    params: tuple = ()
    if account_ids is not None:
        if not account_ids:
            return {}
        placeholders = ",".join("?" for _ in account_ids)
        scope = f" AND account_id IN ({placeholders})"
        params = tuple(account_ids)
    q = f"""
    SELECT r.id, r.kind, r.account_id, r.input_json, r.result_json, r.created_at
    FROM calc_runs r
    JOIN (
        SELECT account_id, MAX(id) AS max_id
        FROM calc_runs
        WHERE account_id IS NOT NULL{scope}
        GROUP BY account_id
    ) m ON r.id = m.max_id
    """
    rows = [dict(r) for r in conn.execute(q, params).fetchall()]
    for row in rows:
        row["result"] = json.loads(row.pop("result_json"))
        row["input"] = json.loads(row.pop("input_json"))
    return {int(row["account_id"]): row for row in rows}


def get(conn: sqlite3.Connection, run_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return dict(row) if row else None
