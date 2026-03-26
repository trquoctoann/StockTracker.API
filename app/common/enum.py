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
