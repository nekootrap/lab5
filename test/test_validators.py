"""Тесты универсального валидатора по аннотациям типов."""

from dataclasses import dataclass

import pytest

from python.models import Address, Product, User
from python.validators import ValidationError, validate, validate_or_raise


def test_valid_object_returns_empty_list():
    user = User(
        name="Анна",
        email="anna@mail.ru",
        address=Address("Ставрополь", "Ленина", "1"),
        products=[Product("Кофе", 350.0, Address("Москва", "Тверская", "7"))],
    )
    assert validate(user) == []


def test_invalid_single_field_returns_one_error():
    addr = Address(city=123, street="Ленина", house="1")  # type: ignore[arg-type]
    errors = validate(addr)
    assert len(errors) == 1
    assert "city" in errors[0]


def test_invalid_multiple_fields_returns_matching_error_count():
    user = User(
        name=None,  # type: ignore[arg-type]
        email=123,  # type: ignore[arg-type]
        address=Address("Ставрополь", "Ленина", "1"),
    )
    errors = validate(user)
    assert len(errors) == 2
    assert any("name" in err for err in errors)
    assert any("email" in err for err in errors)


def test_nested_object_error_detected():
    user = User(
        name="Анна",
        email="anna@mail.ru",
        address=Address("Ставрополь", 42, "1"),  # type: ignore[arg-type]
    )
    errors = validate(user)
    assert len(errors) == 1
    assert "Address.street" in errors[0]


def test_list_elements_validated():
    user = User(
        name="Анна",
        email="anna@mail.ru",
        address=Address("Ставрополь", "Ленина", "1"),
        products=[Product("Кофе", "бесплатно", Address("Москва", "Тверская", "7"))],  # type: ignore[arg-type]
    )
    errors = validate(user)
    assert len(errors) == 1
    assert "Product.price" in errors[0]


def test_validate_or_raise_raises_validation_error():
    bad_addr = Address(city="Ставрополь", street="Ленина", house=10)  # type: ignore[arg-type]
    with pytest.raises(ValidationError) as exc_info:
        validate_or_raise(bad_addr)
    assert "house" in str(exc_info.value)


def test_bool_is_not_accepted_as_int():
    @dataclass
    class Item:
        count: int

    assert validate(Item(count=5)) == []
    errors = validate(Item(count=True))  # type: ignore[arg-type]
    assert len(errors) == 1
    assert "count" in errors[0]
