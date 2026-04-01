from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.user.infrastructure.persistence.user_model import UserRoleModel


class UserFilterField(StrEnum):
    id = "id"
    username = "username"
    email = "email"
    first_name = "first_name"
    last_name = "last_name"
    status = "status"
    record_status = "record_status"
    version = "version"
    created_at = "created_at"
    updated_at = "updated_at"
    created_by = "created_by"
    updated_by = "updated_by"
    user_role_tenant_id = "user_role.tenant_id"
    user_role_id = "user_role.id"


class UserFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in UserFilterField)
    related_filter_specs: ClassVar[dict[str, FilterQueryParameter.RelatedFilterSpec]] = {
        "user_role": FilterQueryParameter.RelatedFilterSpec(
            model=UserRoleModel,
            fk_on_root="id",
            fk_on_related="user_id",
        )
    }


class UserPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in UserFilterField)
