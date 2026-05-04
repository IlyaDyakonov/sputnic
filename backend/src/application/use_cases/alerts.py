from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.alert_repo import AlertRepository
from src.models import Alert


class AlertService:
    def __init__(self, session: AsyncSession):
        self.repo = AlertRepository(session)

    async def list_alerts(self) -> list[Alert]:
        return await self.repo.list_alerts()

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)
        return await self.repo.create(alert)
