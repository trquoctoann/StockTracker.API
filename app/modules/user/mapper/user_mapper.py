from __future__ import annotations

from app.common.base_mapper import BaseMapper
from app.modules.user.domain.user_entity import UserEntity, UserRoleEntity
from app.modules.user.infrastructure.persistence.user_model import UserModel, UserRoleModel


class UserMapper(BaseMapper[UserModel, UserEntity]):
    model_class = UserModel
    entity_class = UserEntity


class UserRoleMapper(BaseMapper[UserRoleModel, UserRoleEntity]):
    model_class = UserRoleModel
    entity_class = UserRoleEntity
