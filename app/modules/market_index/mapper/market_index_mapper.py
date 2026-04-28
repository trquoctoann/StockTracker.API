from app.common.base_mapper import BaseMapper
from app.modules.market_index.domain.market_index_entity import IndexCompositionEntity, MarketIndexEntity
from app.modules.market_index.infrastructure.persistence.market_index_model import (
    IndexCompositionModel,
    MarketIndexModel,
)


class MarketIndexMapper(BaseMapper[MarketIndexModel, MarketIndexEntity]):
    model_class = MarketIndexModel
    entity_class = MarketIndexEntity


class IndexCompositionMapper(BaseMapper[IndexCompositionModel, IndexCompositionEntity]):
    model_class = IndexCompositionModel
    entity_class = IndexCompositionEntity
