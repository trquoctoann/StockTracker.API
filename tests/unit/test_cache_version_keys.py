import uuid

from app.common.cache_version_keys import (
    get_role_version_cache_key,
    get_user_cache_key,
    get_user_role_version_cache_key,
    get_user_version_cache_key,
)


class TestGetUserCacheKey:
    def test_with_uuid(self):
        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        assert get_user_cache_key(uid) == f"user:{uid}"

    def test_with_string(self):
        assert get_user_cache_key("abc") == "user:abc"


class TestGetUserVersionCacheKey:
    def test_format(self):
        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        assert get_user_version_cache_key(uid) == f"user:{uid}:version"


class TestGetUserRoleVersionCacheKey:
    def test_with_tenant_id(self):
        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        result = get_user_role_version_cache_key(uid, "ADMIN", 5)
        assert result == f"user_role:{uid}:ADMIN:5:version"

    def test_without_tenant_id(self):
        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        result = get_user_role_version_cache_key(uid, "TENANT", None)
        assert result == f"user_role:{uid}:TENANT:null:version"


class TestGetRoleVersionCacheKey:
    def test_format(self):
        assert get_role_version_cache_key(42) == "role:42:version"

    def test_zero_id(self):
        assert get_role_version_cache_key(0) == "role:0:version"
