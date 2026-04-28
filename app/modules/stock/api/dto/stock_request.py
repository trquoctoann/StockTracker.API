from app.modules.stock.application.command.stock_command import CreateStockCommand as StockCreateRequest


class StockUpdateRequest(StockCreateRequest):
    pass


__all__ = ["StockCreateRequest", "StockUpdateRequest"]
