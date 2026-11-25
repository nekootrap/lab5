"""Реестр сериализуемых классов и метакласс SerializableMeta.

См. лекцию 5: слайд 7 (регистрация классов), слайд 8 (модификация классов),
слайд 9 (практические примеры метаклассов).
"""

from typing import Any

# Глобальный реестр: имя класса -> класс.
REGISTRY: dict[str, type] = {}


class SerializableMeta(type):
    """Метакласс: регистрирует классы в REGISTRY и добавляет метод to_dict.

    Подключение: class User(metaclass=SerializableMeta): ...
    (для dataclass-моделей — дополнительный аргумент metaclass=...)
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs):
        raise NotImplementedError("SerializableMeta.__new__: требуется реализовать")


class Serializable:
    """Базовый класс: регистрация и добавление to_dict через __init_subclass__."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        raise NotImplementedError("__init_subclass__: требуется реализовать")


def get_class(name: str) -> type:
    """Возвращает класс из реестра по имени.

    Raises:
        KeyError: если класс с таким именем не зарегистрирован.
    """
    raise NotImplementedError("get_class: требуется реализовать")


def registered_classes() -> dict[str, type]:
    """Возвращает копию реестра (защиту реестра от внешних изменений
    обеспечивает возврат копии, а не самого словаря)."""
    raise NotImplementedError("registered_classes: требуется реализовать")
