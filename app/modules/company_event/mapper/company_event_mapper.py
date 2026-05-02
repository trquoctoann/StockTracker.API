from app.common.base_mapper import BaseMapper
from app.modules.company_event.domain.company_event_entity import CompanyEventEntity
from app.modules.company_event.infrastructure.persistence.company_event_model import CompanyEventModel


class CompanyEventMapper(BaseMapper[CompanyEventModel, CompanyEventEntity]):
    model_class = CompanyEventModel
    entity_class = CompanyEventEntity
