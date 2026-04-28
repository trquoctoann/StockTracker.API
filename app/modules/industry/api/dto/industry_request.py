from app.modules.industry.application.command.industry_command import CreateIndustryCommand as IndustryCreateRequest


class IndustryUpdateRequest(IndustryCreateRequest):
    pass


__all__ = ["IndustryCreateRequest", "IndustryUpdateRequest"]
