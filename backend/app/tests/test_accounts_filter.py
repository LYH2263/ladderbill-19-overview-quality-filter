import pytest
from fastapi import HTTPException

from app import seed
from app.routers import accounts as accounts_router
from app.services.billing_service import BillingService


@pytest.fixture(scope="module", autouse=True)
def _seeded():
    seed.init_db()


def _payload(quality):
    with BillingService() as svc:
        return svc.list_accounts(quality)


def test_no_filter_returns_all_accounts():
    data = _payload(None)
    assert data["quality"] is None
    assert data["total_count"] == 3
    assert data["filtered_count"] == 3
    assert data["filtered_count"] == len(data["items"])


def test_dirty_filter_count_and_membership():
    data = _payload("dirty")
    assert data["quality"] == "dirty"
    assert data["total_count"] == 3
    assert data["filtered_count"] == 1
    assert data["filtered_count"] == len(data["items"])
    assert all("种子" in a["name"] for a in data["items"])
    assert data["items"][0]["meter_no"] == "M-1002"


def test_clean_filter_count_and_membership():
    data = _payload("clean")
    assert data["quality"] == "clean"
    assert data["filtered_count"] == 2
    assert data["filtered_count"] == len(data["items"])
    assert all("种子" not in a["name"] for a in data["items"])
    assert {a["meter_no"] for a in data["items"]} == {"M-1001", "M-1003"}


def _by_meter(items, meter_no):
    return next(a for a in items if a["meter_no"] == meter_no)


def test_latest_run_bill_summary():
    data = _payload(None)
    a1 = _by_meter(data["items"], "M-1001")
    summary = a1["latest_run"]
    assert summary["kind"] == "bill"
    assert summary["total"] == 62.40
    assert summary["kwh"] == 120


def test_latest_run_compare_uses_peak_total():
    data = _payload(None)
    a2 = _by_meter(data["items"], "M-1002")
    summary = a2["latest_run"]
    assert summary["kind"] == "compare"
    assert summary["total"] == 309.60
    assert summary["peak_total"] == 309.60
    assert summary["plain_total"] == 258.00


def test_account_without_run_has_empty_summary():
    data = _payload("clean")
    a3 = _by_meter(data["items"], "M-1003")
    assert a3["latest_run"] == {}
    # 无运行的户仍在名单内
    assert data["filtered_count"] == len(data["items"]) == 2


def test_invalid_quality_raises_readable_error():
    with pytest.raises(HTTPException) as exc:
        accounts_router.list_accounts(quality="weird")
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "invalid_quality"
    assert "dirty" in exc.value.detail["allowed"]
    assert "clean" in exc.value.detail["allowed"]
