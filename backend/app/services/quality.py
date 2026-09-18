"""户号质量过滤：名称带“种子”标记的对照户记为 dirty，其余为 clean。"""

DIRTY_MARKER = "种子"
QUALITY_FILTERS = ("all", "clean", "dirty")


def is_dirty(account: dict) -> bool:
    return DIRTY_MARKER in (account.get("name") or "")


def apply_quality(accounts: list[dict], quality: str) -> list[dict]:
    if quality == "dirty":
        return [a for a in accounts if is_dirty(a)]
    if quality == "clean":
        return [a for a in accounts if not is_dirty(a)]
    return list(accounts)
