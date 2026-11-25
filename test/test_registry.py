"""Тесты метакласса SerializableMeta, __init_subclass__ и реестра классов."""

import pytest

from python.registry import (
    REGISTRY,
    Serializable,
    SerializableMeta,
    get_class,
    registered_classes,
)


def test_metaclass_registers_class_in_registry():
    class TempModelA(metaclass=SerializableMeta):
        def __init__(self, title: str) -> None:
            self.title = title

    assert "TempModelA" in REGISTRY
    assert REGISTRY["TempModelA"] is TempModelA


def test_get_class_returns_registered_or_raises_key_error():
    class TempModelB(metaclass=SerializableMeta):
        pass

    assert get_class("TempModelB") is TempModelB
    with pytest.raises(KeyError):
        get_class("NonExistentClassXYZ")


def test_registered_classes_returns_copy():
    snapshot = registered_classes()
    snapshot["InjectedFake"] = dict
    assert "InjectedFake" not in REGISTRY


def test_metaclass_adds_to_dict_method():
    class TempProduct(metaclass=SerializableMeta):
        def __init__(self, name: str, price: float) -> None:
            self.name = name
            self.price = price

    item = TempProduct("Кофе", 350.0)
    assert item.to_dict() == {
        "__class__": "TempProduct",
        "name": "Кофе",
        "price": 350.0,
    }


def test_metaclass_preserves_custom_to_dict():
    class CustomModel(metaclass=SerializableMeta):
        def to_dict(self):
            return {"custom": True}

    assert CustomModel().to_dict() == {"custom": True}


def test_plain_class_without_metaclass_not_registered():
    class PlainClass:
        pass

    assert "PlainClass" not in REGISTRY


def test_init_subclass_alternative_registers_and_adds_to_dict():
    class AltProduct(Serializable):
        def __init__(self, name: str, qty: int) -> None:
            self.name = name
            self.qty = qty

    assert get_class("AltProduct") is AltProduct
    assert AltProduct("Чай", 2).to_dict() == {
        "__class__": "AltProduct",
        "name": "Чай",
        "qty": 2,
    }
