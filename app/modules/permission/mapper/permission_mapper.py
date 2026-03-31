from app.common.base_mapper import BaseMapper
from app.modules.permission.domain.permission_entity import PermissionEntity
from app.modules.permission.infrastructure.persistence.permission_model import PermissionModel


class PermissionMapper(BaseMapper[PermissionModel, PermissionEntity]):
    model_class = PermissionModel
    entity_class = PermissionEntity
