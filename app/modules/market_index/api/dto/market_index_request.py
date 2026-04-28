from app.modules.market_index.application.command.market_index_command import (
    CreateMarketIndexCommand as MarketIndexCreateRequest,
)


class MarketIndexUpdateRequest(MarketIndexCreateRequest):
    pass


__all__ = ["MarketIndexCreateRequest", "MarketIndexUpdateRequest"]
