"""Тесты универсального сериализатора и десериализатора."""

import datetime

import pytest

from python.models import Address, Product, User
from python.serializers import SKIP_FIELDS, from_dict, to_dict


@pytest.mark.parametrize("value", [42, 3.14, "привет", True, False, None])
def test_primitives_unchanged(value):
    assert to_dict(value) == value


def test_datetime_converted_to_iso_string():
    dt = datetime.datetime(2024, 5, 10, 14, 30, 0)
    assert to_dict(dt) == "2024-05-10T14:30:00"


def test_roundtrip_nested_user():
    user = User(
        name="Анна",
        email="anna@mail.ru",
        address=Address("Ставрополь", "Ленина", "1"),
        registered=datetime.datetime(2024, 1, 1, 12, 0, 0),
        products=[
            Product("Кофе", 350.0, Address("Москва", "Тверская", "7")),
            Product("Чай", 200.5, Address("Казань", "Баумана", "12")),
        ],
    )

    serialized = to_dict(user)
    assert serialized["__class__"] == "User"
    assert serialized["address"]["__class__"] == "Address"
    assert serialized["registered"] == "2024-01-01T12:00:00"
    assert serialized["products"][0]["warehouse"]["city"] == "Москва"

    restored = from_dict(User, serialized)
    assert restored == user
    assert restored is not user


def test_private_attributes_excluded():
    class Account:
        def __init__(self, login: str, secret: str) -> None:
            self.login = login
            self._secret = secret

    result = to_dict(Account("user1", "hidden"))
    assert result == {"__class__": "Account", "login": "user1"}
    assert "_secret" not in result


def test_skip_fields_excluded():
    class Credentials:
        def __init__(self, username: str, password: str) -> None:
            self.username = username
            self.password = password

    assert "password" in SKIP_FIELDS
    result = to_dict(Credentials("admin", "qwerty"))
    assert result == {"__class__": "Credentials", "username": "admin"}
    assert "password" not in result


def test_unsupported_type_raises_type_error():
    with pytest.raises(TypeError):
        to_dict(object())


def test_from_dict_missing_required_field_raises_key_error():
    incomplete = {"city": "Ставрополь", "street": "Ленина"}
    with pytest.raises(KeyError):
        from_dict(Address, incomplete)


def test_from_dict_ignores_extra_keys_and_checks_nested_type():
    data = {"city": "Ставрополь", "street": "Ленина", "house": "1", "extra": 999}
    addr = from_dict(Address, data)
    assert addr == Address("Ставрополь", "Ленина", "1")

    bad_user_data = {
        "name": "Анна",
        "email": "anna@mail.ru",
        "address": "Ставрополь",
    }
    with pytest.raises(TypeError):
        from_dict(User, bad_user_data)


def test_to_dict_circular_reference_protection():
    user = User("Анна", "a@x.ru", Address("Ставрополь", "Ленина", "1"))
    user.self_ref = user
    result = to_dict(user)
    assert result["self_ref"] == "<circular: User>"
