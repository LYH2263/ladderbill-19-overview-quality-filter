from fastapi import APIRouter, HTTPException

from app.services.billing_service import BillingService
from app.services.quality import QUALITY_FILTERS

router = APIRouter(tags=["accounts"])


@router.get("/accounts")
def list_accounts(quality: str = "all"):
    if quality not in QUALITY_FILTERS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_QUALITY_FILTER",
                "message": (
                    f"unsupported quality filter {quality!r}; "
                    f"expected one of: {', '.join(QUALITY_FILTERS)}"
                ),
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
