from pydantic import BaseModel

from app.modules.company_event.application.command.company_event_command import (
    CreateCompanyEventCommand,
)


class CompanyEventSyncRequest(BaseModel):
    items: list[CreateCompanyEventCommand]


__all__ = ["CompanyEventSyncRequest"]
