from pydantic import BaseModel

from app.modules.company_affiliation.application.command.company_affiliation_command import (
    CreateCompanyAffiliationCommand,
)


class CompanyAffiliationSyncRequest(BaseModel):
    items: list[CreateCompanyAffiliationCommand]


__all__ = ["CompanyAffiliationSyncRequest"]
