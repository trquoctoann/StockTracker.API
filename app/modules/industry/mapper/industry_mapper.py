from app.common.base_mapper import BaseMapper
from app.modules.industry.domain.industry_entity import IndustryEntity
from app.modules.industry.infrastructure.persistence.industry_model import IndustryModel


class IndustryMapper(BaseMapper[IndustryModel, IndustryEntity]):
    model_class = IndustryModel
    entity_class = IndustryEntity
