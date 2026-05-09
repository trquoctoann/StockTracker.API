from enum import Enum


class RecordStatus(Enum):
    ENABLED = "ENABLED"
    DELETED = "DELETED"


class UserStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class RoleType(Enum):
    DEFAULT = "DEFAULT"
    CUSTOM = "CUSTOM"


class RoleScope(Enum):
    ADMIN = "ADMIN"
    TENANT = "TENANT"


class StockExchange(Enum):
    UPCOM = "UPCOM"
    HSX = "HSX"
    DELISTED = "DELISTED"
    HNX = "HNX"
    BOND = "BOND"


class StockType(Enum):
    STOCK = "STOCK"
    BOND = "BOND"
    FU = "FU"
    DEBENTURE = "DEBENTURE"
    ETF = "ETF"
    UNIT_TRUST = "UNIT_TRUST"
    CW = "CW"


class PriceInterval(Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"


class MatchType(Enum):
    BUY = "BUY"
    SELL = "SELL"
