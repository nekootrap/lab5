"""Реестр сериализуемых классов и метакласс SerializableMeta.

См. лекцию 5: слайд 7 (регистрация классов), слайд 8 (модификация классов),
слайд 9 (практические примеры метаклассов).
"""

from dataclasses import dataclass
from typing import Any

# Глобальный реестр: имя класса -> класс.
REGISTRY: dict[str, type] = {}


def _make_to_dict():
    """Создаёт метод экземпляра to_dict, делегирующий в python.serializers.to_dict."""

    def to_dict(self: Any) -> Any:
        from python.serializers import to_dict as serializers_to_dict

        return serializers_to_dict(self)

    return to_dict


class SerializableMeta(type):
    """Метакласс: регистрирует классы в REGISTRY и добавляет метод to_dict.

    При повторной регистрации класса с тем же именем запись в REGISTRY
    перезаписывается (удобно для интерактивной работы и повторных объявлений в тестах).
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs: Any):
        # Добавляем to_dict в namespace ДО создания класса, если класс не определил свой
        if "to_dict" not in namespace:
            namespace["to_dict"] = _make_to_dict()

        # Передача mcs первым аргументом обязательна
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        REGISTRY[name] = cls
        return cls


class Serializable:
    """Базовый класс: регистрация и добавление to_dict через __init_subclass__."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "to_dict" not in cls.__dict__:
            cls.to_dict = _make_to_dict()
        REGISTRY[cls.__name__] = cls


def get_class(name: str) -> type:
    """Возвращает класс из реестра по имени.

    Raises:
        KeyError: если класс с таким именем не зарегистрирован.
    """
    if name not in REGISTRY:
        raise KeyError(f"Класс '{name}' не найден в реестре")
    return REGISTRY[name]


def registered_classes() -> dict[str, type]:
    """Возвращает копию реестра (защиту реестра от внешних изменений
    обеспечивает возврат копии, а не самого словаря)."""
    return dict(REGISTRY)


# Демонстрационные классы для проверки реестра и метакласса
@dataclass
class ProductV2(metaclass=SerializableMeta):
    """Демонстрационная модель товара с метаклассом SerializableMeta."""

    name: str
    price: float


@dataclass
class UserV2(metaclass=SerializableMeta):
    """Демонстрационная модель пользователя с метаклассом SerializableMeta."""

    name: str
    email: str
