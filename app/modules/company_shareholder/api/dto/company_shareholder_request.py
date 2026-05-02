from pydantic import BaseModel

from app.modules.company_shareholder.application.command.company_shareholder_command import (
    CreateCompanyShareholderCommand,
)


class CompanyShareholderSyncRequest(BaseModel):
    items: list[CreateCompanyShareholderCommand]


__all__ = ["CompanyShareholderSyncRequest"]
