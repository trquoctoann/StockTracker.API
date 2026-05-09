from app.common.base_mapper import BaseMapper
from app.modules.stock_price_history.domain.stock_price_history_entity import StockPriceHistoryEntity
from app.modules.stock_price_history.infrastructure.persistence.stock_price_history_model import (
    StockPriceHistoryModel,
)


class StockPriceHistoryMapper(BaseMapper[StockPriceHistoryModel, StockPriceHistoryEntity]):
    model_class = StockPriceHistoryModel
    entity_class = StockPriceHistoryEntity
