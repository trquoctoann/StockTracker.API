from app.common.base_mapper import BaseMapper
from app.modules.stock_intraday.domain.stock_intraday_entity import StockIntradayEntity
from app.modules.stock_intraday.infrastructure.persistence.stock_intraday_model import StockIntradayModel


class StockIntradayMapper(BaseMapper[StockIntradayModel, StockIntradayEntity]):
    model_class = StockIntradayModel
    entity_class = StockIntradayEntity
