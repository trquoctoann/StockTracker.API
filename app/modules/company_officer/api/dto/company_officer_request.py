from pydantic import BaseModel

from app.modules.company_officer.application.command.company_officer_command import (
    CreateCompanyOfficerCommand,
)


class CompanyOfficerSyncRequest(BaseModel):
    items: list[CreateCompanyOfficerCommand]


__all__ = ["CompanyOfficerSyncRequest"]
