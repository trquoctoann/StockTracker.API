from pydantic import BaseModel

from app.modules.company_news.application.command.company_news_command import (
    CreateCompanyNewsCommand,
)


class CompanyNewsSyncRequest(BaseModel):
    items: list[CreateCompanyNewsCommand]


__all__ = ["CompanyNewsSyncRequest"]
