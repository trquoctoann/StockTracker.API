from app.common.base_mapper import BaseMapper
from app.modules.role.domain.role_entity import RoleEntity, RolePermissionEntity
from app.modules.role.infrastructure.persistence.role_model import RoleModel, RolePermissionModel


class RoleMapper(BaseMapper[RoleModel, RoleEntity]):
    model_class = RoleModel
    entity_class = RoleEntity


class RolePermissionMapper(BaseMapper[RolePermissionModel, RolePermissionEntity]):
    model_class = RolePermissionModel
    entity_class = RolePermissionEntity
