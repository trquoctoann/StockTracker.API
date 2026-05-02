from app.common.base_mapper import BaseMapper
from app.modules.company_shareholder.domain.company_shareholder_entity import CompanyShareholderEntity
from app.modules.company_shareholder.infrastructure.persistence.company_shareholder_model import (
    CompanyShareholderModel,
)


class CompanyShareholderMapper(BaseMapper[CompanyShareholderModel, CompanyShareholderEntity]):
    model_class = CompanyShareholderModel
    entity_class = CompanyShareholderEntity
