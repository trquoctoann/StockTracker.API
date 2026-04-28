from app.common.base_mapper import BaseMapper
from app.modules.stock.domain.stock_entity import StockEntity, StockIndustryEntity
from app.modules.stock.infrastructure.persistence.stock_model import StockIndustryModel, StockModel


class StockMapper(BaseMapper[StockModel, StockEntity]):
    model_class = StockModel
    entity_class = StockEntity


class StockIndustryMapper(BaseMapper[StockIndustryModel, StockIndustryEntity]):
    model_class = StockIndustryModel
    entity_class = StockIndustryEntity
