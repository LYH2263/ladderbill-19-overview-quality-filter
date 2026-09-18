from fastapi import APIRouter, HTTPException

from app.services.billing_service import BillingService

router = APIRouter(tags=["accounts"])

ALLOWED_QUALITY = ("dirty", "clean")


@router.get("/accounts")
def list_accounts(quality: str | None = None):
    if quality is not None and quality not in ALLOWED_QUALITY:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_quality",
                "message": f"不支持的质量过滤值 {quality!r}，仅支持 dirty（偏高种子）或 clean（正常）",
                "allowed": list(ALLOWED_QUALITY),
            },
        )
    with BillingService() as svc:
        return svc.list_accounts(quality)


@router.get("/accounts/{account_id}")
def get_account(account_id: int):
    with BillingService() as svc:
        row = svc.get_account(account_id)
        if not row:
            raise HTTPException(404, "account not found")
        readings = svc.readings_for_account(account_id)
        return {"account": row, "readings": readings}
