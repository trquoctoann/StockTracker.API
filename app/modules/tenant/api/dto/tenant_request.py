from app.modules.tenant.application.command.tenant_command import (
    CreateTenantCommand as TenantCreateRequest,
)


class TenantUpdateRequest(TenantCreateRequest):
    pass


__all__ = ["TenantCreateRequest", "TenantUpdateRequest"]
