from fastapi import APIRouter

from src.application.use_cases.files import list_alerts
from src.schemas import AlertItem

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertItem])
async def list_alerts_view():
    return await list_alerts()
