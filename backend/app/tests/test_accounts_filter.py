"""质量过滤：/api/accounts?quality= 的过滤、计数、最近运行摘要与错误码。"""

import os
import tempfile

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="ladderbill-test-"))

import pytest
from fastapi.testclient import TestClient

from app import seed
from app.db import connect
from app.main import app

TABLES = ("calc_runs", "readings", "accounts", "tiers", "settings")


@pytest.fixture()
def client():
    seed.init_db()  # 首次运行时建表
    conn = connect()
    for table in TABLES:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    seed.init_db()  # 重新播种，保证户号 id 与抄表/运行记录对应
    with TestClient(app) as c:
        yield c


def test_default_lists_all_with_total(client):
    body = client.get("/api/accounts").json()
    assert body["quality"] == "all"
    assert body["total"] == 2
    assert len(body["items"]) == body["total"]


def test_filter_dirty(client):
    body = client.get("/api/accounts", params={"quality": "dirty"}).json()
    assert body["quality"] == "dirty"
    assert body["total"] == len(body["items"]) == 1
    assert "种子" in body["items"][0]["name"]


def test_filter_clean(client):
    body = client.get("/api/accounts", params={"quality": "clean"}).json()
    assert body["quality"] == "clean"
    assert body["total"] == len(body["items"]) == 1
    assert "种子" not in body["items"][0]["name"]


def test_latest_run_summary_carries_totals(client):
    body = client.get("/api/accounts").json()
    summaries = {i["name"]: i["run_summary"] for i in body["items"]}
    bill = summaries["张家"]
    assert bill["kind"] == "bill"
    assert bill["total"] == 62.40
    compare = summaries["李家(种子偏高)"]
    assert compare["kind"] == "compare"
    assert compare["peak_total"] == 309.60
    assert compare["delta"] == 51.60


def test_account_without_runs_keeps_empty_summary(client):
    conn = connect()
    conn.execute("INSERT INTO accounts(name, meter_no, note) VALUES ('王家', 'M-1003', '无运行记录')")
    conn.commit()
    conn.close()
    body = client.get("/api/accounts").json()
    assert body["total"] == 3
    item = next(i for i in body["items"] if i["name"] == "王家")
    assert item["run_summary"] == {}


def test_invalid_quality_returns_readable_error(client):
    r = client.get("/api/accounts", params={"quality": "bogus"})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert detail["code"] == "INVALID_QUALITY_FILTER"
    assert "bogus" in detail["message"]
    assert "clean" in detail["message"]
    assert "dirty" in detail["message"]
