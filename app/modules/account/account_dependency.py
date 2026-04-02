from typing import Annotated

from fastapi import Depends

from app.modules.account.application.account_domain_service import AccountDomainService
from app.modules.account.application.account_query_service import AccountQueryService
from app.modules.user.user_dependency import UserDomainServiceDep


def get_account_query_service() -> AccountQueryService:
    return AccountQueryService()


def get_account_domain_service(user_domain_service: UserDomainServiceDep) -> AccountDomainService:
    return AccountDomainService(user_domain_service)


AccountQueryServiceDep = Annotated[AccountQueryService, Depends(get_account_query_service)]
AccountDomainServiceDep = Annotated[AccountDomainService, Depends(get_account_domain_service)]
