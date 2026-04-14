import pytest

from app.common.auth.permission_codes import PermissionBitmap, PermissionCode


@pytest.fixture()
def bitmap():
    return PermissionBitmap()


class TestToBitmap:
    def test_empty_set_returns_zero(self, bitmap: PermissionBitmap):
        assert bitmap.to_bitmap(set()) == 0

    def test_single_permission_sets_correct_bit(self, bitmap: PermissionBitmap):
        result = bitmap.to_bitmap({PermissionCode.USER_READ})
        assert result == 1 << 0

    def test_multiple_permissions(self, bitmap: PermissionBitmap):
        result = bitmap.to_bitmap({PermissionCode.USER_READ, PermissionCode.USER_CREATE})
        assert result == (1 << 0) | (1 << 1)

    def test_all_permissions(self, bitmap: PermissionBitmap):
        all_codes = {p.value for p in PermissionCode}
        result = bitmap.to_bitmap(all_codes)
        expected = (1 << len(PermissionCode)) - 1
        assert result == expected

    def test_unknown_code_is_ignored(self, bitmap: PermissionBitmap):
        result = bitmap.to_bitmap({"NON_EXISTENT_CODE"})
        assert result == 0

    def test_mixed_known_and_unknown(self, bitmap: PermissionBitmap):
        result = bitmap.to_bitmap({PermissionCode.ROLE_READ, "FAKE_CODE"})
        assert result == bitmap.to_bitmap({PermissionCode.ROLE_READ})


class TestHasPermissions:
    def test_has_permission_returns_true(self, bitmap: PermissionBitmap):
        bm = bitmap.to_bitmap({PermissionCode.USER_READ, PermissionCode.USER_CREATE})
        assert bitmap.has_permissions(bm, {PermissionCode.USER_READ}) is True

    def test_missing_permission_returns_false(self, bitmap: PermissionBitmap):
        bm = bitmap.to_bitmap({PermissionCode.USER_READ})
        assert bitmap.has_permissions(bm, {PermissionCode.USER_DELETE}) is False

    def test_empty_required_returns_true(self, bitmap: PermissionBitmap):
        assert bitmap.has_permissions(0, set()) is True

    def test_requires_all_permissions(self, bitmap: PermissionBitmap):
        bm = bitmap.to_bitmap({PermissionCode.USER_READ})
        assert bitmap.has_permissions(bm, {PermissionCode.USER_READ, PermissionCode.USER_CREATE}) is False

    def test_zero_bitmap_denies_everything(self, bitmap: PermissionBitmap):
        assert bitmap.has_permissions(0, {PermissionCode.USER_READ}) is False

    def test_unknown_required_code_returns_false(self, bitmap: PermissionBitmap):
        bm = bitmap.to_bitmap({PermissionCode.USER_READ})
        assert bitmap.has_permissions(bm, {"UNKNOWN"}) is False


class TestBitmapRoundTrip:
    def test_encode_decode_all_individual_codes(self, bitmap: PermissionBitmap):
        for code in PermissionCode:
            bm = bitmap.to_bitmap({code.value})
            assert bitmap.has_permissions(bm, {code.value}) is True

    def test_idempotent_encoding(self, bitmap: PermissionBitmap):
        codes = {PermissionCode.TENANT_READ, PermissionCode.TENANT_CREATE}
        assert bitmap.to_bitmap({p.value for p in codes}) == bitmap.to_bitmap({p.value for p in codes})
