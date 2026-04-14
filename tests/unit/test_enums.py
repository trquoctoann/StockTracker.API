from app.common.enum import RecordStatus, RoleScope, RoleType, UserStatus


class TestRecordStatus:
    def test_values(self):
        assert RecordStatus.ENABLED.value == "ENABLED"
        assert RecordStatus.DELETED.value == "DELETED"

    def test_member_count(self):
        assert len(RecordStatus) == 2


class TestUserStatus:
    def test_values(self):
        assert UserStatus.PENDING.value == "PENDING"
        assert UserStatus.ACTIVE.value == "ACTIVE"
        assert UserStatus.INACTIVE.value == "INACTIVE"


class TestRoleType:
    def test_values(self):
        assert RoleType.DEFAULT.value == "DEFAULT"
        assert RoleType.CUSTOM.value == "CUSTOM"


class TestRoleScope:
    def test_values(self):
        assert RoleScope.ADMIN.value == "ADMIN"
        assert RoleScope.TENANT.value == "TENANT"
