from app.common.base_mapper import BaseMapper
from app.modules.company_officer.domain.company_officer_entity import CompanyOfficerEntity
from app.modules.company_officer.infrastructure.persistence.company_officer_model import CompanyOfficerModel


class CompanyOfficerMapper(BaseMapper[CompanyOfficerModel, CompanyOfficerEntity]):
    model_class = CompanyOfficerModel
    entity_class = CompanyOfficerEntity
