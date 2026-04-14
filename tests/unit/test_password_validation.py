import pytest
from pydantic import ValidationError

from app.modules.user.application.command.user_command import CreateUserCommand


def _valid_payload(**overrides) -> dict:
    base = {
        "username": "johndoe",
        "password": "Strong1!pass",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }
    base.update(overrides)
    return base


class TestPasswordStrengthValidator:
    def test_valid_password_accepted(self):
        cmd = CreateUserCommand(**_valid_payload(password="Abcdef1!"))
        assert cmd.password == "Abcdef1!"

    def test_password_without_uppercase_rejected(self):
        with pytest.raises((ValidationError, Exception)):
            CreateUserCommand(**_valid_payload(password="abcdef1!"))

    def test_password_without_digit_rejected(self):
        with pytest.raises((ValidationError, Exception)):
            CreateUserCommand(**_valid_payload(password="Abcdefgh!"))

    def test_password_without_special_char_rejected(self):
        with pytest.raises((ValidationError, Exception)):
            CreateUserCommand(**_valid_payload(password="Abcdefg1"))

    def test_password_too_short_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserCommand(**_valid_payload(password="Ab1!"))

    def test_password_too_long_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserCommand(**_valid_payload(password="A1!" + "a" * 126))

    def test_minimum_valid_password(self):
        cmd = CreateUserCommand(**_valid_payload(password="Aa1!aaaa"))
        assert len(cmd.password) == 8

    def test_password_with_all_criteria(self):
        cmd = CreateUserCommand(**_valid_payload(password="MyP@ss99"))
        assert cmd.password == "MyP@ss99"


class TestCreateUserCommandValidation:
    def test_valid_command(self):
        cmd = CreateUserCommand(**_valid_payload())
        assert cmd.username == "johndoe"
        assert cmd.email == "john@example.com"

    def test_empty_username_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserCommand(**_valid_payload(username=""))

    def test_empty_first_name_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserCommand(**_valid_payload(first_name=""))

    def test_last_name_can_be_none(self):
        cmd = CreateUserCommand(**_valid_payload(last_name=None))
        assert cmd.last_name is None

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserCommand(**_valid_payload(email="not-an-email"))

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserCommand(**_valid_payload(unknown_field="x"))
