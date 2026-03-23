from enum import Enum


class RecordStatus(Enum):
    ENABLED = "enabled"
    DELETED = "deleted"


class UserStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class RoleType(Enum):
    DEFAULT = "default"
    CUSTOM = "custom"


class RoleScope(Enum):
    ADMIN = "admin"
    TENANT = "tenant"
