from app.common.base_repository import RepositoryPort
from app.modules.tenant.domain.tenant_entity import TenantEntity


class TenantRepository(RepositoryPort[TenantEntity]):
    pass
