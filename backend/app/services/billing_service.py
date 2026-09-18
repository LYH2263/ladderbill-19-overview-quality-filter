import json

from app.db import connect
from app.engines.peak_compare import compare_plain_vs_peak
from app.engines.tier_progressive import calc_bill
from app.repositories import accounts as accounts_repo
from app.repositories import readings as readings_repo
from app.repositories import runs as runs_repo
from app.repositories import settings as settings_repo
from app.repositories import tiers as tiers_repo
from app.services import quality as quality_mod


def _run_summary(run: dict) -> dict:
    """最近运行的合计摘要：run 元信息 + 结果中带有的合计字段。"""
    result = json.loads(run.get("result_json") or "{}")
    summary = {"run_id": run["id"], "kind": run["kind"], "created_at": run["created_at"]}
    for key in ("total", "plain_total", "peak_total", "delta"):
        if key in result:
            summary[key] = result[key]
    return summary


class BillingService:
    def __init__(self):
        self._conn = connect()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def list_accounts(self, quality: str = "all") -> dict:
        accounts = quality_mod.apply_quality(accounts_repo.list_all(self._conn), quality)
        latest_runs = runs_repo.latest_by_account(self._conn)
        items = []
        for account in accounts:
            run = latest_runs.get(account["id"])
            # 无最近运行的户保留在名单内，摘要为空对象
            items.append({**account, "run_summary": _run_summary(run) if run else {}})
        return {"quality": quality, "total": len(items), "items": items}

    def get_account(self, account_id: int):
        return accounts_repo.get(self._conn, account_id)

    def list_tiers(self):
        return tiers_repo.list_ordered(self._conn)

    def list_readings(self):
        return readings_repo.list_all(self._conn)

    def readings_for_account(self, account_id: int):
        return readings_repo.for_account(self._conn, account_id)

    def settings_map(self):
        return settings_repo.get_map(self._conn)

    def run_bill(self, kwh: float, peak: bool, account_id: int | None, persist: bool):
        tiers = tiers_repo.as_calc_rows(self._conn)
        pf = settings_repo.peak_factor(self._conn)
        factor = pf if peak else 1.0
        result = calc_bill(kwh, tiers, factor)
        run_id = None
        if persist:
            run_id = runs_repo.insert(
                self._conn,
                "bill",
                {"kwh": kwh, "peak": peak, "account_id": account_id},
                result,
                account_id,
            )
        return {"run_id": run_id, **result}

    def run_compare(self, kwh: float, persist: bool):
        tiers = tiers_repo.as_calc_rows(self._conn)
        pf = settings_repo.peak_factor(self._conn)
        result = compare_plain_vs_peak(kwh, tiers, pf)
        run_id = None
        if persist:
            run_id = runs_repo.insert(self._conn, "compare", {"kwh": kwh}, result, None)
        return {"run_id": run_id, **result}

    def list_history(self, limit: int = 50):
        return runs_repo.list_recent(self._conn, limit)

    def get_run(self, run_id: int):
        return runs_repo.get(self._conn, run_id)

    def dashboard_stats(self):
        accounts = accounts_repo.list_all(self._conn)
        readings = readings_repo.list_all(self._conn)
        return {
            "account_count": len(accounts),
            "reading_count": len(readings),
            "clean_accounts": len(quality_mod.apply_quality(accounts, "clean")),
            "dirty_accounts": len(quality_mod.apply_quality(accounts, "dirty")),
            "recent_runs": len(runs_repo.list_recent(self._conn, 5)),
        }
