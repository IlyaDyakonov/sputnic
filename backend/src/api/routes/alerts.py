from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.dependencies import get_alert_service
from src.application.use_cases.alerts import AlertService
from src.schemas import AlertItem

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertItem])
async def list_alerts_view(alert_service: Annotated[AlertService, Depends(get_alert_service)]):
    return await alert_service.list_alerts()
