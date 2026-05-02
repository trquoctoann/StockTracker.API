from app.common.base_mapper import BaseMapper
from app.modules.company_news.domain.company_news_entity import CompanyNewsEntity
from app.modules.company_news.infrastructure.persistence.company_news_model import CompanyNewsModel


class CompanyNewsMapper(BaseMapper[CompanyNewsModel, CompanyNewsEntity]):
    model_class = CompanyNewsModel
    entity_class = CompanyNewsEntity
