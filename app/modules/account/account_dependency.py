from typing import Annotated

from fastapi import Depends

from app.common.auth.context_token_codec import ContextTokenCodecDep
from app.modules.account.application.account_domain_service import AccountDomainService
from app.modules.account.application.account_query_service import AccountQueryService
from app.modules.role.role_dependency import RoleQueryServiceDep
from app.modules.user.user_dependency import UserDomainServiceDep, UserQueryServiceDep


def get_account_query_service() -> AccountQueryService:
    return AccountQueryService()


def get_account_domain_service(
    user_domain_service: UserDomainServiceDep,
    user_query_service: UserQueryServiceDep,
    role_query_service: RoleQueryServiceDep,
    context_token_codec: ContextTokenCodecDep,
) -> AccountDomainService:
    return AccountDomainService(user_domain_service, user_query_service, role_query_service, context_token_codec)


AccountQueryServiceDep = Annotated[AccountQueryService, Depends(get_account_query_service)]
AccountDomainServiceDep = Annotated[AccountDomainService, Depends(get_account_domain_service)]
