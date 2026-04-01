from __future__ import annotations

from app.common.base_mapper import BaseMapper
from app.modules.tenant.domain.tenant_entity import TenantEntity
from app.modules.tenant.infrastructure.persistence.tenant_model import TenantModel


class TenantMapper(BaseMapper[TenantModel, TenantEntity]):
    model_class = TenantModel
    entity_class = TenantEntity
