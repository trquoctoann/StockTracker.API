from app.common.base_schema import BaseResponse
from app.common.enum import RoleScope


class AccountSwitchContextResponse(BaseResponse):
    token_type: str
    access_token: str
    expires_in: int
    scope: RoleScope
    tenant_id: int | None = None
