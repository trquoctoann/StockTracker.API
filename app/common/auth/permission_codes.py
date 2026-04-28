from enum import StrEnum


class PermissionCode(StrEnum):
    USER_READ = "USER_READ"
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    USER_MANAGE_ROLES = "USER_MANAGE_ROLES"

    ROLE_READ = "ROLE_READ"
    ROLE_CREATE = "ROLE_CREATE"
    ROLE_UPDATE = "ROLE_UPDATE"
    ROLE_DELETE = "ROLE_DELETE"
    ROLE_MANAGE_PERMISSIONS = "ROLE_MANAGE_PERMISSIONS"

    TENANT_READ = "TENANT_READ"
    TENANT_CREATE = "TENANT_CREATE"
    TENANT_UPDATE = "TENANT_UPDATE"
    TENANT_DELETE = "TENANT_DELETE"

    INDUSTRY_READ = "INDUSTRY_READ"
    INDUSTRY_CREATE = "INDUSTRY_CREATE"
    INDUSTRY_UPDATE = "INDUSTRY_UPDATE"
    INDUSTRY_DELETE = "INDUSTRY_DELETE"

    STOCK_READ = "STOCK_READ"
    STOCK_CREATE = "STOCK_CREATE"
    STOCK_UPDATE = "STOCK_UPDATE"
    STOCK_DELETE = "STOCK_DELETE"


class PermissionBitmap:
    def __init__(self) -> None:
        self._index_map = {code: idx for idx, code in enumerate([p.value for p in PermissionCode])}

    def to_bitmap(self, permission_codes: set[str]) -> int:
        bitmap = 0
        for code in permission_codes:
            index = self._index_map.get(code)
            if index is None:
                continue
            bitmap |= 1 << index
        return bitmap

    def has_permissions(self, bitmap: int, required_codes: set[str]) -> bool:
        return all(self._is_granted(bitmap, code) for code in required_codes)

    def _is_granted(self, bitmap: int, code: str) -> bool:
        index = self._index_map.get(code)
        if index is None:
            return False
        return (bitmap & (1 << index)) != 0


permission_bitmap = PermissionBitmap()
