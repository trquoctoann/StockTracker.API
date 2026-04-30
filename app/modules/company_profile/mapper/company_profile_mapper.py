from app.common.base_mapper import BaseMapper
from app.modules.company_profile.domain.company_profile_entity import CompanyProfileEntity
from app.modules.company_profile.infrastructure.persistence.company_profile_model import CompanyProfileModel


class CompanyProfileMapper(BaseMapper[CompanyProfileModel, CompanyProfileEntity]):
    model_class = CompanyProfileModel
    entity_class = CompanyProfileEntity
