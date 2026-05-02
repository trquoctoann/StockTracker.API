from app.common.base_mapper import BaseMapper
from app.modules.company_affiliation.domain.company_affiliation_entity import CompanyAffiliationEntity
from app.modules.company_affiliation.infrastructure.persistence.company_affiliation_model import (
    CompanyAffiliationModel,
)


class CompanyAffiliationMapper(BaseMapper[CompanyAffiliationModel, CompanyAffiliationEntity]):
    model_class = CompanyAffiliationModel
    entity_class = CompanyAffiliationEntity
